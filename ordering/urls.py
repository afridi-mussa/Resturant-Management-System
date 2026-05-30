"""
URL routes for the ordering app.

Each path() maps a URL pattern to a view. The name="..." is an internal label
used by {% url 'name' %} in templates and redirect("name") in views, so URLs
can change without breaking links.
"""
from django.contrib.auth import views as auth_views      # ready-made login/logout views
from django.urls import include, path
from rest_framework.routers import DefaultRouter         # auto-generates API URLs

from . import views

# The router builds all the REST API URLs for the viewset automatically,
# e.g. /api/menu/ (list) and /api/menu/<id>/ (detail).
router = DefaultRouter()
router.register(r"menu", views.MenuItemViewSet, basename="api-menu")

urlpatterns = [
    # REST API (mounted under /api/ by the include below)
    path("api/", include(router.urls)),

    # Menu (Read) - open to everyone
    path("", views.MenuListView.as_view(), name="menu_list"),
    path(
        "menu/<int:pk>/",                       # <int:pk> = the item's id from the URL
        views.MenuItemDetailView.as_view(),
        name="menu_item_detail",
    ),

    # Menu (Create / Update / Delete) - admin only
    path("menu/add/", views.MenuItemCreateView.as_view(), name="menu_item_add"),
    path(
        "menu/<int:pk>/edit/",
        views.MenuItemUpdateView.as_view(),
        name="menu_item_edit",
    ),
    path(
        "menu/<int:pk>/delete/",
        views.MenuItemDeleteView.as_view(),
        name="menu_item_delete",
    ),

    # Orders (placing + customer history)
    path("order/place/", views.place_order, name="place_order"),
    path("my-orders/", views.OrderListView.as_view(), name="my_orders"),

    # Order management (admin only)
    path("manage/orders/", views.ManageOrdersView.as_view(), name="manage_orders"),
    path(
        "manage/orders/<int:pk>/status/",      # POST target for status changes
        views.update_order_status,
        name="update_order_status",
    ),

    # User profile
    path("profile/", views.profile, name="profile"),
    path("profile/password/", views.change_password, name="change_password"),

    # Authentication (register is custom; login/logout reuse Django's views)
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="ordering/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
