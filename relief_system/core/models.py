from django.conf import settings
from django.db import models
from django.utils import timezone


class UserProfile(models.Model):
    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        DONOR = "DONOR", "Donor"
        RECIPIENT = "RECIPIENT", "Recipient"
        COORDINATOR = "COORDINATOR", "Logistics Coordinator"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
    )

    def __str__(self) -> str:
        return f"{self.user.get_username()} ({self.get_role_display()})"


class Donation(models.Model):
    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="donations",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    location = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.title


class Request(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="requests",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    location = models.CharField(max_length=255)
    is_fulfilled = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.title


class Delivery(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_TRANSIT = "IN_TRANSIT", "In Transit"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    donation = models.ForeignKey(
        Donation,
        on_delete=models.CASCADE,
        related_name="deliveries",
    )
    request = models.ForeignKey(
        Request,
        on_delete=models.CASCADE,
        related_name="deliveries",
    )
    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="coordinated_deliveries",
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    pickup_time = models.DateTimeField(null=True, blank=True)
    dropoff_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"Delivery #{self.pk} - {self.get_status_display()}"


class TransparencyReport(models.Model):
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_reports",
    )
    generated_at = models.DateTimeField(default=timezone.now)
    total_donations = models.PositiveIntegerField()
    total_requests = models.PositiveIntegerField()
    total_deliveries = models.PositiveIntegerField()
    delivered_count = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"Report {self.generated_at:%Y-%m-%d %H:%M}"

from django.db import models

class TestModel(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name