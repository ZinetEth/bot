from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import transaction as db_transaction

from .models import Transaction
from .serializers import TransactionSerializer, TransactionApprovalSerializer
from apps.CustomerUsers.permissions import IsAdmin, IsStaff
from apps.mifos.services import MifosService # Forward import for Mifos integration

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().select_related('user', 'approved_by')
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            # Users can create their own transactions (e.g., submitting payment proof)
            self.permission_classes = [IsAuthenticated] 
        elif self.action in ['list', 'retrieve']:
            # Admin, Staff, and the user themselves can view transactions
            self.permission_classes = [IsAuthenticated, (IsAdmin | IsStaff)]
            if self.action == 'retrieve':
                # Allow users to view their own specific transaction
                self.permission_classes = [IsAuthenticated]
        elif self.action in ['approve', 'reject']:
            self.permission_classes = [IsAuthenticated, IsAdmin] # Only Admin can approve/reject
        else:
            self.permission_classes = [IsAuthenticated, IsAdmin] # Default for other actions (update, destroy)

        return super().get_permissions()

    def perform_create(self, serializer):
        amount = serializer.validated_data['amount']
        method = serializer.validated_data['method']
        
        # Initial status is PENDING, unless auto-posted
        initial_status = 'PENDING'
        auto_posted = False

        if method == 'Telebirr' and amount <= 15000:
            initial_status = 'APPROVED' # Mark as approved for potential auto-posting
            auto_posted = True
            # Attempt to post to Mifos immediately
            # This part will call the MifosService
            try:
                # Assuming MifosService has a method like `deposit_to_savings`
                # You'll need to pass appropriate data like user's Mifos account ID
                # For now, this is a placeholder
                # mifos_response = MifosService.deposit_to_savings(self.request.user.mifos_account_id, amount)
                # if mifos_response.success:
                #     initial_status = 'POSTED'
                # else:
                #     # Handle Mifos error, revert to APPROVED or PENDING for manual review
                #     initial_status = 'APPROVED' 
                pass # Placeholder for Mifos integration
                initial_status = 'POSTED' # Assume success for now
            except Exception as e:
                # Log the error and keep status as APPROVED for manual review
                print(f"Error auto-posting to Mifos: {e}")
                initial_status = 'APPROVED'
                auto_posted = False # If auto-post failed, it's no longer 'auto_posted' successfully

        transaction = serializer.save(
            user=self.request.user,
            status=initial_status,
            auto_posted=auto_posted
        )
        
        # If transaction is auto-posted and approved, trigger share purchase if applicable
        if transaction.status == 'POSTED':
            from apps.shares.services import ShareService
            ShareService.process_share_purchase_from_transaction(transaction)


    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        transaction = self.get_object()
        # Only allow approval if status is PENDING or REJECTED
        if transaction.status not in ['PENDING', 'REJECTED']:
            return Response({"detail": "Transaction cannot be approved from its current status."}, 
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = TransactionApprovalSerializer(data={'status': 'APPROVED'})
        serializer.is_valid(raise_exception=True)
        
        with db_transaction.atomic():
            transaction.status = 'APPROVED'
            transaction.approved_by = request.user
            transaction.approved_at = timezone.now()
            transaction.rejection_reason = None
            transaction.save()

            # Attempt to post to Mifos X
            try:
                # MifosService.deposit_to_savings(transaction.user.mifos_account_id, transaction.amount)
                # For now, just change status to POSTED
                transaction.status = 'POSTED'
                transaction.save()
                # Trigger share purchase after successful posting to Mifos
                from apps.shares.services import ShareService
                ShareService.process_share_purchase_from_transaction(transaction)
            except Exception as e:
                print(f"Error posting transaction {transaction.id} to Mifos: {e}")
                # If Mifos posting fails, revert status to APPROVED for manual follow-up
                transaction.status = 'APPROVED'
                transaction.save()
                return Response({"detail": "Transaction approved, but failed to post to Mifos X.", "error": str(e)}, 
                                status=status.HTTP_200_OK)

        return Response(self.get_serializer(transaction).data)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        transaction = self.get_object()
        # Only allow rejection if status is PENDING or APPROVED (if an approved one needs to be reversed)
        if transaction.status not in ['PENDING', 'APPROVED']:
            return Response({"detail": "Transaction cannot be rejected from its current status."}, 
                            status=status.HTTP_400)