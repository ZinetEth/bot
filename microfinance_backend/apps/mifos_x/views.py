from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from apps.CustomUser.permissions import IsAdmin
from .services import MifosService

class MifosStatusView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin] # Only Admins can check Mifos status

    def get(self, request, *args, **kwargs):
        """
        A simple endpoint to check if Mifos X API is reachable.
        """
        try:
            # Attempt a simple GET request to a public Mifos endpoint, e.g., 'offices'
            # This is just a test; a real health check might be more robust.
            MifosService._make_api_call('GET', 'offices')
            return Response({"status": "Mifos X API is reachable."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "Mifos X API is not reachable", "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)