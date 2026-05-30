"""
Views for the BistroSaaS ordering app.

A "view" receives a web request and returns a web response (usually an HTML
page or a redirect). This file mixes two styles:
    - Function-Based Views (FBVs): plain functions, e.g. register(), place_order()
    - Class-Based Views (CBVs): reusable classes, e.g. MenuListView, OrderListView
"""
from django.contrib import messages                       # one-time flash messages (success/error)
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required  # blocks anonymous users from FBVs
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin  # same, for CBVs
from django.db.models import Q                            # lets us build OR queries
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy                      # build a URL by its name (lazily)
from django.views.decorators.http import require_POST     # only allow POST requests
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from rest_framework import viewsets                       # DRF: bundles list/create/update/delete
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .forms import (
    CustomerProfileForm,
    MenuItemForm,
    RegisterForm,
    StyledSetPasswordForm,
    UserInfoForm,
)
from .models import Category, CustomerProfile, MenuItem, Order
from .serializers import MenuItemSerializer


# --- Authentication ---

def register(request):
    """Sign up a new user (Customer or Admin) and log them in immediately."""
    # If somebody who is already logged in hits this page, send them to the menu.
    if request.user.is_authenticated:
        return redirect("menu_list")

    if request.method == "POST":
        # The form was submitted -> validate the data the user typed.
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()                  # create the User (RegisterForm sets admin flags)
            login(request, user)                # start a logged-in session right away
            role_label = "Admin" if user.is_superuser else "Customer"
            messages.success(
                request,
                f"Welcome, {user.username}! Your {role_label} account was created.",
            )
            return redirect("menu_list")
    else:
        # First visit (GET) -> show an empty form.
        form = RegisterForm()

    return render(request, "ordering/register.html", {"form": form})


# --- Admin-only access mixin ---

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Reusable gate: only logged-in superusers (our 'Admin' role) may continue."""

    def test_func(self):
        # UserPassesTestMixin calls this; returning False blocks the request.
        return self.request.user.is_superuser

    def handle_no_permission(self):
        # Decide what happens when the test fails.
        if self.request.user.is_authenticated:
            # Logged in but not an admin -> friendly message + back to menu.
            messages.error(
                self.request, "You do not have permission to manage menu items."
            )
            return redirect("menu_list")
        # Not logged in at all -> default behaviour (redirect to the login page).
        return super().handle_no_permission()


# --- MenuItem CRUD (Create, Read, Update, Delete) ---

class MenuListView(ListView):
    """Public menu page with search, category filtering and pagination."""

    model = MenuItem
    template_name = "ordering/menu_list.html"
    context_object_name = "items"      # name used for the list inside the template
    paginate_by = 6                    # show 6 items per page

    def get_queryset(self):
        # Start with only items that are marked available.
        # select_related("category") fetches the category in the same SQL query (faster).
        queryset = MenuItem.objects.filter(is_available=True).select_related(
            "category"
        )

        # ?q=... -> search by name OR description (Q objects allow the OR).
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

        # ?category=<id> -> keep only items in that category.
        category = self.request.GET.get("category", "").strip()
        if category:
            queryset = queryset.filter(category__id=category)

        return queryset.order_by("category__name", "name")

    def get_context_data(self, **kwargs):
        # Add extra values the template needs (filter buttons + remembering the inputs).
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["search_query"] = self.request.GET.get("q", "")
        context["selected_category"] = self.request.GET.get("category", "")
        return context


class MenuItemDetailView(DetailView):
    """Single dish detail page (loads the item by its primary key from the URL)."""

    model = MenuItem
    template_name = "ordering/menu_item_detail.html"
    context_object_name = "item"


class MenuItemCreateView(AdminRequiredMixin, CreateView):
    """Admin-only form to add a new menu item (handles the image upload too)."""

    model = MenuItem
    form_class = MenuItemForm
    template_name = "ordering/menu_item_form.html"
    success_url = reverse_lazy("menu_list")   # where to go after a successful save

    def form_valid(self, form):
        # Runs only when submitted data is valid -> show a success message.
        messages.success(self.request, "Menu item created successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        # The form template is shared with the edit view; this sets the heading.
        context = super().get_context_data(**kwargs)
        context["title"] = "Add Menu Item"
        return context


class MenuItemUpdateView(AdminRequiredMixin, UpdateView):
    """Admin-only form to edit an existing menu item."""

    model = MenuItem
    form_class = MenuItemForm
    template_name = "ordering/menu_item_form.html"  # same template as create
    success_url = reverse_lazy("menu_list")

    def form_valid(self, form):
        messages.success(self.request, "Menu item updated successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Edit Menu Item"
        return context


class MenuItemDeleteView(AdminRequiredMixin, DeleteView):
    """Admin-only confirmation page that deletes a menu item on POST."""

    model = MenuItem
    template_name = "ordering/menu_item_confirm_delete.html"
    success_url = reverse_lazy("menu_list")
    context_object_name = "item"

    def form_valid(self, form):
        messages.success(self.request, "Menu item deleted successfully.")
        return super().form_valid(form)


# --- Orders ---

@login_required  # only logged-in users can place orders
def place_order(request):
    """Show available items as checkboxes (GET) and create an order (POST)."""
    available_items = MenuItem.objects.filter(is_available=True).select_related(
        "category"
    )

    if request.method == "POST":
        # getlist() because several checkboxes share the name "items".
        selected_ids = request.POST.getlist("items")
        # Re-filter against available items so users can't order hidden/invalid ids.
        selected_items = available_items.filter(id__in=selected_ids)

        if not selected_items:
            messages.error(request, "Please select at least one item to order.")
            return redirect("place_order")

        # Server-side total (never trust a price sent by the browser).
        total = sum(item.price for item in selected_items)

        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            status=Order.Status.PENDING,     # new orders always start as Pending
        )
        order.items.set(selected_items)      # attach the chosen items (many-to-many)

        messages.success(
            request,
            f"Order #{order.pk} placed successfully! Total: ${total}.",
        )
        return redirect("my_orders")

    return render(
        request, "ordering/place_order.html", {"items": available_items}
    )


class OrderListView(LoginRequiredMixin, ListView):
    """The customer's own order history ('My Orders')."""

    model = Order
    template_name = "ordering/order_list.html"
    context_object_name = "orders"
    paginate_by = 10

    def get_queryset(self):
        # Only this user's orders; prefetch_related avoids 1 query per order's items.
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("items")
            .order_by("-created_at")          # newest first
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Collect ids of orders the admin just updated, so the template can
        # highlight them. list(...) forces the query to run NOW (before we clear
        # the flag below in get()).
        updated_orders = Order.objects.filter(
            user=self.request.user, unseen_update=True
        )
        context["updated_order_ids"] = list(
            updated_orders.values_list("id", flat=True)
        )
        return context

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # Mark the customer's status updates as "seen" now that they're viewing.
        Order.objects.filter(user=request.user, unseen_update=True).update(
            unseen_update=False
        )
        return response


# --- Admin order management / confirmation ---

class ManageOrdersView(AdminRequiredMixin, ListView):
    """Admin dashboard listing ALL orders, with an optional status filter."""

    model = Order
    template_name = "ordering/manage_orders.html"
    context_object_name = "orders"
    paginate_by = 15

    def get_queryset(self):
        queryset = Order.objects.select_related("user").prefetch_related(
            "items"
        )
        # ?status=Pending (etc.) narrows the list.
        status = self.request.GET.get("status", "").strip()
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = Order.Status.choices       # for the filter buttons
        context["selected_status"] = self.request.GET.get("status", "")
        return context


@require_POST       # status changes must come from a form POST, not a plain link
@login_required
def update_order_status(request, pk):
    """Admin action: change an order's status and flag the customer for a notification."""
    # Extra safety check (the template hides this from non-admins, but never trust that alone).
    if not request.user.is_superuser:
        messages.error(request, "You do not have permission to manage orders.")
        return redirect("menu_list")

    order = get_object_or_404(Order, pk=pk)              # 404 if the order doesn't exist
    new_status = request.POST.get("status")
    valid_statuses = [choice[0] for choice in Order.Status.choices]

    # Reject anything that isn't one of our four allowed statuses.
    if new_status not in valid_statuses:
        messages.error(request, "Invalid order status.")
        return redirect("manage_orders")

    order.status = new_status
    order.unseen_update = True                           # triggers the customer's notification
    order.save()

    messages.success(
        request,
        f"Order #{order.pk} marked as {new_status}.",
    )
    return redirect("manage_orders")


# --- REST API ---

class MenuItemViewSet(viewsets.ModelViewSet):
    """Exposes MenuItem data as JSON via the REST API (the bonus feature).

    A ModelViewSet auto-creates list/detail/create/update/delete endpoints.
    IsAuthenticatedOrReadOnly = anyone can READ, only logged-in users can WRITE.
    """

    queryset = MenuItem.objects.select_related("category").all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# --- User profile ---

@login_required
def profile(request):
    """View/edit personal info: name + email (User) and phone/address/picture (profile)."""
    # get_or_create guarantees a profile exists even for older accounts.
    profile_obj, _ = CustomerProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # Two forms saved together: one for the User, one for the CustomerProfile.
        # request.FILES is required for the uploaded profile picture.
        user_form = UserInfoForm(request.POST, instance=request.user)
        profile_form = CustomerProfileForm(
            request.POST, request.FILES, instance=profile_obj
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile was updated successfully.")
            return redirect("profile")
    else:
        # Pre-fill both forms with the current values.
        user_form = UserInfoForm(instance=request.user)
        profile_form = CustomerProfileForm(instance=profile_obj)

    return render(
        request,
        "ordering/profile.html",
        {"user_form": user_form, "profile_form": profile_form},
    )


@login_required
def change_password(request):
    """Let a logged-in user set a new password (new + confirm, no old password)."""
    if request.method == "POST":
        form = StyledSetPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Without this, changing the password would log the user out.
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was changed successfully.")
            return redirect("profile")
    else:
        form = StyledSetPasswordForm(user=request.user)

    return render(request, "ordering/change_password.html", {"form": form})
