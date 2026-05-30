"""
Database models for the BistroSaaS ordering app.

This file defines the 4 main database tables and their relationships:
    CustomerProfile  -> one-to-one  with User
    Category         -> groups menu items
    MenuItem         -> many-to-one with Category
    Order            -> many-to-one with User, many-to-many with MenuItem
"""
from django.db import models
from django.contrib.auth.models import User           # Django's built-in user table
from django.db.models.signals import post_save        # Signal fired after a model is saved
from django.dispatch import receiver                   # Decorator used to "listen" to signals


class CustomerProfile(models.Model):
    """Extra information attached to each User (Django's User has no phone/address)."""

    # OneToOne: every User has exactly one profile. CASCADE = delete profile if user is deleted.
    # related_name="profile" lets us write `user.profile` to reach this object.
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    phone = models.CharField(max_length=20, blank=True)      # blank=True -> optional in forms
    address = models.TextField(blank=True)
    # ImageField stores the file path in the DB; the file itself goes to MEDIA_ROOT/profile_pics/
    profile_pic = models.ImageField(
        upload_to="profile_pics/", blank=True, null=True
    )

    def __str__(self):
        # Controls how the object is shown in the admin and shell (human-readable label).
        return f"{self.user.username}'s Profile"


class Category(models.Model):
    """A food category, e.g. 'Burgers', 'Drinks'. One category has many menu items."""

    name = models.CharField(max_length=100, unique=True)     # unique=True -> no duplicate names
    description = models.TextField(blank=True)

    class Meta:
        # Fix Django's default pluralization ("Categorys") in the admin.
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    """A single dish on the menu. Belongs to exactly one Category."""

    # ForeignKey = the "many" side of one-to-many. Deleting a category deletes its items.
    # related_name="items" lets us write `category.items.all()`.
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="items"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # DecimalField is used for money (avoids floating-point rounding errors).
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to="menu_items/", blank=True, null=True)
    # Controls whether the item shows on the public menu and can be ordered.
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (${self.price})"


class Order(models.Model):
    """A customer's order. Linked to one User and many MenuItems."""

    class Status(models.TextChoices):
        # TextChoices = a fixed set of allowed values shown as a dropdown in forms/admin.
        # Format: CONSTANT = "stored value", "human label"
        PENDING = "Pending", "Pending"
        PREPARING = "Preparing", "Preparing"
        COMPLETED = "Completed", "Completed"
        CANCELLED = "Cancelled", "Cancelled"

    # Which user placed the order. related_name="orders" -> `user.orders.all()`.
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders"
    )
    # ManyToMany: one order can have many items, and one item can be in many orders.
    items = models.ManyToManyField(MenuItem, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)     # set once, when the row is created
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    # Set to True when an admin changes the status, so the customer can be
    # notified. Reset to False once the customer views their orders.
    unseen_update = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)         # updated on every save()

    def __str__(self):
        return f"Order #{self.pk} - {self.user.username} ({self.status})"


# --- Signal: automatically create/keep a CustomerProfile for every User ---
# @receiver connects this function to the post_save signal of the User model,
# so it runs automatically every time a User is saved.
@receiver(post_save, sender=User)
def create_or_update_customer_profile(sender, instance, created, **kwargs):
    if created:
        # A brand-new user was just created -> make their profile.
        CustomerProfile.objects.create(user=instance)
    else:
        # Existing user was updated -> make sure a profile exists, then save it.
        CustomerProfile.objects.get_or_create(user=instance)
        instance.profile.save()
