from django.contrib import admin

from .models import UserProfile, Donation, Request, Delivery, TransparencyReport


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email")


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("title", "donor", "category", "quantity", "location", "is_active", "created_at")
    list_filter = ("category", "is_active", "created_at")
    search_fields = ("title", "description", "location", "donor__username")


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ("title", "recipient", "category", "quantity", "location", "is_fulfilled", "created_at")
    list_filter = ("category", "is_fulfilled", "created_at")
    search_fields = ("title", "description", "location", "recipient__username")


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ("id", "donation", "request", "coordinator", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("donation__title", "request__title", "coordinator__username")


@admin.register(TransparencyReport)
class TransparencyReportAdmin(admin.ModelAdmin):
    list_display = (
        "generated_at",
        "generated_by",
        "total_donations",
        "total_requests",
        "total_deliveries",
        "delivered_count",
    )
    list_filter = ("generated_at",)
