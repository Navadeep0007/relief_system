from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("signup/", views.signup, name="signup"),
    # Donations
    path("donations/", views.donation_list, name="donation_list"),
    path("donations/new/", views.donation_create, name="donation_create"),
    path("donations/<int:pk>/edit/", views.donation_update, name="donation_update"),
    path("donations/<int:pk>/toggle/", views.donation_toggle_active, name="donation_toggle_active"),
    # Requests
    path("requests/", views.request_list, name="request_list"),
    path("requests/new/", views.request_create, name="request_create"),
    path("requests/<int:pk>/edit/", views.request_update, name="request_update"),
    # Deliveries
    path("deliveries/", views.delivery_list, name="delivery_list"),
    path("deliveries/new/", views.delivery_create, name="delivery_create"),
    path("deliveries/<int:pk>/status/", views.delivery_update_status, name="delivery_update_status"),
    # Reports
    path("reports/transparency/", views.transparency_report, name="transparency_report"),
]

