from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    DeliveryForm,
    DeliveryStatusForm,
    DonationForm,
    RequestForm,
    SignUpForm,
)
from .models import Delivery, Donation, Request, TransparencyReport, UserProfile


def get_user_role(user) -> str | None:
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return UserProfile.Roles.ADMIN
    try:
        return user.profile.role
    except UserProfile.DoesNotExist:
        return None


def require_role(user, allowed_roles: tuple[str, ...]) -> bool:
    role = get_user_role(user)
    return role in allowed_roles


def home(request):
    if request.user.is_authenticated:
        return redirect("core:dashboard")
    return render(request, "core/home.html")


def signup(request):
    if request.user.is_authenticated:
        return redirect("core:dashboard")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data["role"]
            UserProfile.objects.create(user=user, role=role)
            login(request, user)
            messages.success(request, "Account created successfully.")
            return redirect("core:dashboard")
    else:
        form = SignUpForm()
    return render(request, "core/signup.html", {"form": form})


@login_required
def dashboard(request):
    role = get_user_role(request.user)

    context: dict = {"role": role}

    if role == UserProfile.Roles.DONOR:
        donations = Donation.objects.filter(donor=request.user).order_by("-created_at")
        context["donations"] = donations
    elif role == UserProfile.Roles.RECIPIENT:
        requests_qs = Request.objects.filter(recipient=request.user).order_by("-created_at")
        deliveries = Delivery.objects.filter(request__recipient=request.user).order_by("-created_at")
        context["requests"] = requests_qs
        context["deliveries"] = deliveries
    elif role == UserProfile.Roles.COORDINATOR:
        deliveries = Delivery.objects.all().order_by("-created_at")
        context["deliveries"] = deliveries
    else:
        # Admin or unknown: show high-level counts
        context.update(
            {
                "donation_count": Donation.objects.count(),
                "request_count": Request.objects.count(),
                "delivery_count": Delivery.objects.count(),
                "delivered_count": Delivery.objects.filter(
                    status=Delivery.Status.DELIVERED
                ).count(),
            }
        )

    return render(request, "core/dashboard.html", context)


@login_required
def donation_list(request):
    role = get_user_role(request.user)
    if role == UserProfile.Roles.DONOR:
        donations = Donation.objects.filter(donor=request.user).order_by("-created_at")
    elif role in (UserProfile.Roles.ADMIN, UserProfile.Roles.COORDINATOR):
        donations = Donation.objects.all().order_by("-created_at")
    else:
        raise PermissionDenied
    return render(request, "core/donation_list.html", {"donations": donations, "role": role})


@login_required
def donation_create(request):
    if not require_role(request.user, (UserProfile.Roles.DONOR, UserProfile.Roles.ADMIN)):
        raise PermissionDenied

    if request.method == "POST":
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.donor = request.user
            donation.save()
            messages.success(request, "Donation created successfully.")
            return redirect("core:donation_list")
    else:
        form = DonationForm()
    return render(request, "core/donation_form.html", {"form": form})


@login_required
def donation_update(request, pk: int):
    donation = get_object_or_404(Donation, pk=pk)
    role = get_user_role(request.user)
    if not (
        role in (UserProfile.Roles.ADMIN, UserProfile.Roles.COORDINATOR)
        or (role == UserProfile.Roles.DONOR and donation.donor_id == request.user.id)
    ):
        raise PermissionDenied

    if request.method == "POST":
        form = DonationForm(request.POST, instance=donation)
        if form.is_valid():
            form.save()
            messages.success(request, "Donation updated successfully.")
            return redirect("core:donation_list")
    else:
        form = DonationForm(instance=donation)
    return render(request, "core/donation_form.html", {"form": form, "donation": donation})


@login_required
def donation_toggle_active(request, pk: int):
    donation = get_object_or_404(Donation, pk=pk)
    role = get_user_role(request.user)
    if not (
        role in (UserProfile.Roles.ADMIN, UserProfile.Roles.COORDINATOR)
        or (role == UserProfile.Roles.DONOR and donation.donor_id == request.user.id)
    ):
        raise PermissionDenied
    donation.is_active = not donation.is_active
    donation.save(update_fields=["is_active"])
    messages.success(request, "Donation status updated.")
    return redirect("core:donation_list")


@login_required
def request_list(request):
    role = get_user_role(request.user)
    if role == UserProfile.Roles.RECIPIENT:
        requests_qs = Request.objects.filter(recipient=request.user).order_by("-created_at")
    elif role in (UserProfile.Roles.ADMIN, UserProfile.Roles.COORDINATOR):
        requests_qs = Request.objects.all().order_by("-created_at")
    else:
        raise PermissionDenied
    return render(request, "core/request_list.html", {"requests": requests_qs, "role": role})


@login_required
def request_create(request):
    if not require_role(request.user, (UserProfile.Roles.RECIPIENT, UserProfile.Roles.ADMIN)):
        raise PermissionDenied

    if request.method == "POST":
        form = RequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.recipient = request.user
            req.save()
            messages.success(request, "Request created successfully.")
            return redirect("core:request_list")
    else:
        form = RequestForm()
    return render(request, "core/request_form.html", {"form": form})


@login_required
def request_update(request, pk: int):
    req = get_object_or_404(Request, pk=pk)
    role = get_user_role(request.user)
    if not (
        role in (UserProfile.Roles.ADMIN, UserProfile.Roles.COORDINATOR)
        or (role == UserProfile.Roles.RECIPIENT and req.recipient_id == request.user.id)
    ):
        raise PermissionDenied

    if request.method == "POST":
        form = RequestForm(request.POST, instance=req)
        if form.is_valid():
            form.save()
            messages.success(request, "Request updated successfully.")
            return redirect("core:request_list")
    else:
        form = RequestForm(instance=req)
    return render(request, "core/request_form.html", {"form": form, "request_obj": req})


@login_required
def delivery_list(request):
    role = get_user_role(request.user)
    if role == UserProfile.Roles.COORDINATOR:
        deliveries = Delivery.objects.all().order_by("-created_at")
    elif role == UserProfile.Roles.RECIPIENT:
        deliveries = Delivery.objects.filter(request__recipient=request.user).order_by("-created_at")
    elif role == UserProfile.Roles.DONOR:
        deliveries = Delivery.objects.filter(donation__donor=request.user).order_by("-created_at")
    elif role == UserProfile.Roles.ADMIN:
        deliveries = Delivery.objects.all().order_by("-created_at")
    else:
        raise PermissionDenied
    return render(request, "core/delivery_list.html", {"deliveries": deliveries, "role": role})


@login_required
def delivery_create(request):
    if not require_role(request.user, (UserProfile.Roles.COORDINATOR, UserProfile.Roles.ADMIN)):
        raise PermissionDenied

    if request.method == "POST":
        form = DeliveryForm(request.POST)
        if form.is_valid():
            delivery = form.save()
            messages.success(request, "Delivery created successfully.")
            return redirect("core:delivery_list")
    else:
        form = DeliveryForm()

    return render(request, "core/delivery_form.html", {"form": form})


@login_required
def delivery_update_status(request, pk: int):
    delivery = get_object_or_404(Delivery, pk=pk)
    if not require_role(request.user, (UserProfile.Roles.COORDINATOR, UserProfile.Roles.ADMIN)):
        raise PermissionDenied

    if request.method == "POST":
        form = DeliveryStatusForm(request.POST, instance=delivery)
        if form.is_valid():
            form.save()
            messages.success(request, "Delivery status updated.")
            return redirect("core:delivery_list")
    else:
        form = DeliveryStatusForm(instance=delivery)
    return render(
        request,
        "core/delivery_status_form.html",
        {"form": form, "delivery": delivery},
    )


@login_required
def transparency_report(request):
    if not require_role(request.user, (UserProfile.Roles.ADMIN, UserProfile.Roles.COORDINATOR)):
        raise PermissionDenied

    total_donations = Donation.objects.count()
    total_requests = Request.objects.count()
    total_deliveries = Delivery.objects.count()
    delivered_count = Delivery.objects.filter(status=Delivery.Status.DELIVERED).count()

    if request.method == "POST":
        report = TransparencyReport.objects.create(
            generated_by=request.user,
            total_donations=total_donations,
            total_requests=total_requests,
            total_deliveries=total_deliveries,
            delivered_count=delivered_count,
        )
        messages.success(request, f"Report generated at {report.generated_at:%Y-%m-%d %H:%M}.")
        return redirect("core:transparency_report")

    recent_reports = TransparencyReport.objects.order_by("-generated_at")[:10]

    # Additional breakdown for transparency
    donations_by_category = (
        Donation.objects.values("category").annotate(count=Count("id")).order_by("-count")
    )

    context = {
        "total_donations": total_donations,
        "total_requests": total_requests,
        "total_deliveries": total_deliveries,
        "delivered_count": delivered_count,
        "recent_reports": recent_reports,
        "donations_by_category": donations_by_category,
    }
    return render(request, "core/transparency_report.html", context)

