# microfinance_backend/apps/CustomUser/models.py

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid # For generating unique referral codes

# Define choices for KYC status on CustomUser, mirroring KYCProfile
KYC_STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('APPROVED', 'Approved'),
    ('REJECTED', 'Rejected'),
]

# Define choices for user roles
class UserRoles(models.TextChoices):
    """
    Defines the roles available for users in the system.
    """
    CUSTOMER = 'CUSTOMER', _('Customer')
    STAFF = 'STAFF', _('Staff')
    LOAN_OFFICER = 'LOAN_OFFICER', _('Loan Officer')
    MANAGER = 'MANAGER', _('Manager')
    ADMIN = 'ADMIN', _('Admin')

# --- Custom User Manager ---
class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where username is the unique identifier.
    Handles creation of users and superusers with custom fields.
    """
    def _create_user(self, username, telegram_id, phone_number, password, **extra_fields):
        """
        Creates and saves a User with the given username, telegram_id,
        phone_number and password.
        """
        if not username:
            raise ValueError(_('The Username must be set'))
        if not telegram_id:
            raise ValueError(_('The Telegram ID must be set'))
        if not phone_number:
            raise ValueError(_('The Phone Number must be set'))

        # Pop custom fields from extra_fields
        preferred_language = extra_fields.pop('preferred_language', 'en')
        
        # New name fields
        first_name = extra_fields.pop('first_name', '')
        father_name = extra_fields.pop('father_name', '')
        grand_father_name = extra_fields.pop('grand_father_name', '')

        referral_code = extra_fields.pop('referral_code', str(uuid.uuid4())[:8].upper())
        account_balance = extra_fields.pop('account_balance', 0.00)
        
        # KYC related fields
        is_kyc_verified = extra_fields.pop('is_kyc_verified', False)
        kyc_status = extra_fields.pop('kyc_status', 'PENDING')

        # Role field
        role = extra_fields.pop('role', UserRoles.CUSTOMER) # Default role is Customer


        user = self.model(
            username=username,
            telegram_id=telegram_id,
            phone_number=phone_number,
            preferred_language=preferred_language,
            first_name=first_name,
            father_name=father_name,
            grand_father_name=grand_father_name,
            referral_code=referral_code,
            account_balance=account_balance,
            is_kyc_verified=is_kyc_verified,
            kyc_status=kyc_status,
            role=role, # Pass new field
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, telegram_id, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_kyc_verified', False)
        extra_fields.setdefault('kyc_status', 'PENDING')
        extra_fields.setdefault('role', UserRoles.CUSTOMER) # Default role for regular users
        return self._create_user(username, telegram_id, phone_number, password, **extra_fields)

    def create_superuser(self, username, telegram_id, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_kyc_verified', False)
        extra_fields.setdefault('kyc_status', 'PENDING')
        extra_fields.setdefault('role', UserRoles.ADMIN) # Superusers are Admins


        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self._create_user(username, telegram_id, phone_number, password, **extra_fields)

# --- Custom User Model ---
class CustomUser(AbstractUser):
    # Overriding the default 'email' field to be blank and null if not used
    email = models.EmailField(_('email address'), unique=False, blank=True, null=True)

    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    
    first_name = models.CharField(_("first name"), max_length=150, blank=True, null=True)
    father_name = models.CharField(max_length=150, blank=True, null=True)
    grand_father_name = models.CharField(max_length=150, blank=True, null=True)

    telegram_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    preferred_language = models.CharField(max_length=5, default='en')

    referral_code = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        help_text="Unique code for user referrals."
    )
    account_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text="Current account balance in Birr."
    )
    last_bot_interaction = models.DateTimeField(
        auto_now=True,
        blank=True,
        null=True,
        help_text="Last time this user interacted with the Telegram bot."
    )

    # KYC related fields on CustomUser
    is_kyc_verified = models.BooleanField(
        default=False,
        help_text="Boolean flag indicating if the user's KYC profile has been approved."
    )
    kyc_status = models.CharField(
        max_length=20,
        choices=KYC_STATUS_CHOICES,
        default='PENDING',
        help_text="Current KYC verification status (Pending, Approved, Rejected)."
    )

    # New: Role field
    role = models.CharField(
        max_length=20,
        choices=UserRoles.choices, # Use choices from UserRoles enum
        default=UserRoles.CUSTOMER,
        help_text="The role of the user in the microfinance system."
    )

    # Add related_name to avoid clashes if you customize other AbstractUser fields
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=('groups'),
        blank=True,
        help_text=('The groups this user belongs to. A user will get all permissions '
                   'granted to each of their groups.'),
        related_name="customuser_groups",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=('user permissions'),
        blank=True,
        help_text=('Specific permissions for this user.'),
        related_name="customuser_user_permissions",
        related_query_name="user",
    )

    # Use the custom manager
    objects = CustomUserManager()

    REQUIRED_FIELDS = ['telegram_id', 'phone_number', 'first_name', 'father_name', 'grand_father_name', 'preferred_language']

    @property
    def full_name(self):
        """Returns the full name composed of all parts."""
        return f"{self.first_name} {self.father_name} {self.grand_father_name}".strip()

    def __str__(self):
        return self.username

    def get_balance(self):
        """Returns the user's current account balance."""
        return self.account_balance

    def update_balance(self, amount):
        """Updates the user's account balance."""
        self.account_balance += amount
        self.save(update_fields=['account_balance'])
        return self.account_balance
