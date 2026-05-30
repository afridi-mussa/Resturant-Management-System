"""
Context processor for navbar notifications.

A context processor is a function that returns a dict which Django merges into
the context of EVERY template. We use it so the navbar (in base.html) can show
notification badges on every page without each view passing the data manually.

Registered in settings.py under TEMPLATES -> OPTIONS -> context_processors.
"""
from .models import Order


def notifications(request):
    """Expose order notification counts to every template (navbar)."""
    data = {}
    user = request.user

    # Anonymous visitors get nothing (no badges to show).
    if not user.is_authenticated:
        return data

    if user.is_superuser:
        # Admins see how many orders are still Pending (awaiting confirmation).
        data["pending_orders_count"] = Order.objects.filter(
            status=Order.Status.PENDING
        ).count()
    else:
        # Customers see how many of their orders have unseen status updates.
        data["order_notification_count"] = Order.objects.filter(
            user=user, unseen_update=True
        ).count()

    return data
