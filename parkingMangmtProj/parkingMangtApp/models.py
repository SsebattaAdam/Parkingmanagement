import math
from django.db import models
from django.contrib.auth.models import AbstractUser, User, PermissionsMixin
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models

from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, role="USER", **extra_fields):
        if not username:
            raise ValueError("The Username field must be set")
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        user = self.model(username=username, email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_manager(self, username, email, password=None, **extra_fields):
        """Creates a Manager user"""
        extra_fields.setdefault("is_staff", True)
        return self.create_user(username, email, password, role="MANAGER", **extra_fields)

    def create_superuser(self, username, email, password=None, **extra_fields):
        """Creates a Superuser"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, role="ADMIN", **extra_fields)

class User(AbstractUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        USER = "USER", "User"
        MANAGER = "MANAGER", "Manager"

    role = models.CharField(
        max_length=50,
        choices=Role.choices,
        default=Role.USER  # Default new users to 'USER' unless specified
    )

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.pk:  # If the user is being created
            self.role = self.role or User.Role.USER  # Assign default if not specified
        super().save(*args, **kwargs)

class UserPermission(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userpermission')
    can_view_reports = models.BooleanField(default=False)
    can_manage_branches = models.BooleanField(default=False)
    can_issue_tickets = models.BooleanField(default=False)
    can_register_clients = models.BooleanField(default=False)

    def __str__(self):
        return f"Permissions for {self.user.username}"


class Business(models.Model):
    business_name = models.CharField(max_length=255)
    contact_details = models.TextField(blank=True, null=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    registration_number = models.CharField(max_length=100)
    tax_id = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="businesses_created")
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically store creation time

    def __str__(self):
        return self.business_name
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string

User = get_user_model()

class Branch(models.Model):
    business = models.ForeignKey('Business', on_delete=models.CASCADE, related_name='branches')  
    branch_name = models.CharField(max_length=255)
    location = models.TextField()
    contact_number = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    is_main_branch = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='branches_created')
    created_at = models.DateTimeField(auto_now_add=True)
    manager = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_branch')  
    parking_slot_identifier = models.CharField(max_length=1, default='B')  # Default identifier for parking slots
    number_of_slots = models.PositiveIntegerField(default=50)  # Default number of parking slots

    def __str__(self):
        return f"{self.branch_name} - {self.business.business_name}"

    def create_manager(self, first_name, last_name, email):
        """Creates a manager for the branch with auto-generated credentials."""
        username = f"{first_name.lower()}{last_name.lower()}{get_random_string(5)}"
        password = get_random_string(10)

        # Create the manager with the MANAGER role
        manager = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=User.Role.MANAGER  # Explicitly set the role to MANAGER
        )

        self.manager = manager
        self.save()
        return username, password  # Return credentials for display

    def create_parking_slots(self):
        """Creates parking slots for the branch."""
        for i in range(1, self.number_of_slots + 1):
            slot_number = f"{self.parking_slot_identifier}{i}"
            ParkingSlot.objects.create(
                branch=self,
                slot_number=slot_number,
                is_available=True,
                created_by=self.created_by
            )

class Client(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='clients')  # Each client belongs to a branch
    vehicle_number_plate = models.CharField(max_length=50, unique=True)  # Ensure unique number plates
    created_at = models.DateTimeField(auto_now_add=True)
    registered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='clients_registered')

    def __str__(self):
        return self.vehicle_number_plate

class ParkingSlot(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='parking_slots')  # Each slot belongs to a branch
    slot_number = models.CharField(max_length=50)  # Unique slot identifier per branch
    is_available = models.BooleanField(default=True)  # Whether the slot is available for parking
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='parking_slots_created')

    def __str__(self):
        return f"Slot {self.slot_number} - {self.branch.branch_name} ({'Available' if self.is_available else 'Occupied'})"


from decimal import Decimal
from django.db import models

class ParkingTicket(models.Model):
    client = models.OneToOneField('Client', on_delete=models.CASCADE, related_name='ticket')
    parking_slot = models.ForeignKey('ParkingSlot', on_delete=models.SET_NULL, null=True, related_name='tickets')
    entry_time = models.DateTimeField(auto_now_add=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)  # Store duration in minutes
    fee_to_pay = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    branch = models.ForeignKey('Branch', on_delete=models.CASCADE, related_name='tickets')
    payment_status = models.CharField(max_length=20, default="pending")

    def __str__(self):
        return f"Ticket for {self.client.vehicle_number_plate} at {self.branch.branch_name}"

    def calculate_fee(self):
        if not self.exit_time:
            return Decimal("0.00")  # Cannot calculate fee if exit time is not set

        # Calculate the duration in minutes
        duration = self.exit_time - self.entry_time
        minutes_parked = int(duration.total_seconds() / 60)  # Convert to minutes
        
        # Save the duration in minutes
        self.duration = minutes_parked
        self.save()
        
        # Fetch the hourly rate for the branch
        rate = self.branch.rates.first()
        if rate is None:
            return Decimal("0.00")  # No rate found

        if rate.rate_type == 'hourly':
            # Calculate fee proportionally to minutes parked
            rate_per_minute = Decimal(rate.rate_value) / Decimal(60)  # Convert hourly rate to per-minute rate
            return (Decimal(minutes_parked) * rate_per_minute).quantize(Decimal("0.01"))  # Round to 2 decimal places

        elif rate.rate_type == 'daily':
            days_parked = Decimal(minutes_parked) / Decimal(1440)  # 1440 minutes in a day
            return (days_parked * Decimal(rate.rate_value)).quantize(Decimal("0.01"))

        elif rate.rate_type == 'monthly':
            months_parked = Decimal(minutes_parked) / Decimal(43200)  # 43200 minutes in 30 days
            return (months_parked * Decimal(rate.rate_value)).quantize(Decimal("0.01"))

        return Decimal("0.00")  # Invalid rate type

    @property
    def is_cleared(self):
        return bool(self.exit_time and self.duration)


class ParkingRate(models.Model):
    RATE_CHOICES = [
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
    ]
    rate_type = models.CharField(max_length=10, choices=RATE_CHOICES)
    rate_value = models.DecimalField(max_digits=10, decimal_places=2)  # To store the rate value (e.g., 5.00)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='rates')  # Each rate is tied to a branch

    def __str__(self):
        return f"{self.rate_type.capitalize()} Rate for {self.branch.branch_name} - {self.rate_value}"



class ExpenditureCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='categories_created')

    def __str__(self):
        return self.name

class ExpenditureItem(models.Model):
    category = models.ForeignKey(ExpenditureCategory, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='items_created')

    def __str__(self):
        return self.item_name

class Expenditure(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('mobile_money', 'Mobile Money'),
    ]

    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='expenditures')
    category = models.ForeignKey(ExpenditureCategory, on_delete=models.SET_NULL, null=True, related_name='expenditures')
    item_name = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    proof_of_payment = models.FileField(upload_to='proof_of_payments/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='expenditures_created')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category.name} - {self.amount} ({self.payment_method})"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='cart_items')
    category = models.ForeignKey(ExpenditureCategory, on_delete=models.SET_NULL, null=True)
    item_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)

    def total_cost(self):
        return self.quantity * self.price_per_item

    def __str__(self):
        return f"{self.item_name} ({self.quantity} x {self.price_per_item})"
    
    
class AccountBalance(models.Model):
    branch = models.OneToOneField(Branch, on_delete=models.CASCADE, related_name='account_balance')
    cash = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bank = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mobile_money = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Balances for {self.branch.branch_name}"
    

    User = get_user_model()

class ActivityLog(models.Model):
    ACTIVITY_TYPES = [
        ('expenditure', 'Expenditure'),
        ('balance_update', 'Balance Update'),
        ('user_activity', 'User Activity'),
        ('other', 'Other'),
    ]

    branch = models.ForeignKey('Branch', on_delete=models.CASCADE, related_name='activity_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activity_logs')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    details = models.TextField()
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.activity_type} by {self.user} on {self.timestamp}"