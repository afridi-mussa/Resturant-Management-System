"""
Forms for the BistroSaaS ordering app.

Forms validate user input and (for ModelForms) map directly onto a model so
they can save to the database. Bootstrap CSS classes are attached to widgets
here so the HTML inputs look styled without extra template code.
"""
from django import forms
from django.conf import settings                       # to read ADMIN_SECRET_KEY
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm
from django.contrib.auth.models import User

from .models import CustomerProfile, MenuItem


class RegisterForm(UserCreationForm):
    """Sign-up form that adds a Role choice and an Admin-only Secret Key.

    Extends Django's UserCreationForm (which already handles username + the two
    password fields and password-strength validation).
    """

    ROLE_CUSTOMER = "customer"
    ROLE_ADMIN = "admin"
    ROLE_CHOICES = [
        (ROLE_CUSTOMER, "Customer"),
        (ROLE_ADMIN, "Admin"),
    ]

    # Dropdown to pick the account type. id_role is used by the page's JavaScript
    # to show/hide the secret key field.
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        initial=ROLE_CUSTOMER,
        widget=forms.Select(attrs={"class": "form-select", "id": "id_role"}),
    )
    # Only meaningful when role == admin; rendered as a password input.
    secret_key = forms.CharField(
        required=False,
        label="Secret Key",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Required for Admin registration",
            }
        ),
        help_text="Only required when registering as an Admin.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)      # password fields are added by the parent form

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Bootstrap styling to the inherited auth fields.
        for name in ("username", "password1", "password2"):
            if name in self.fields:
                self.fields[name].widget.attrs.update({"class": "form-control"})

    def clean(self):
        """Extra validation that runs after the standard field checks."""
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        secret_key = cleaned_data.get("secret_key")

        # If the user wants an Admin account, the secret key must match.
        if role == self.ROLE_ADMIN:
            expected = getattr(settings, "ADMIN_SECRET_KEY", "admin123")
            if not secret_key:
                self.add_error(
                    "secret_key", "A secret key is required to register as Admin."
                )
            elif secret_key != expected:
                self.add_error("secret_key", "Invalid secret key.")

        return cleaned_data

    def save(self, commit=True):
        """Create the User, promoting them to superuser if they chose Admin."""
        user = super().save(commit=False)   # build the object but don't hit the DB yet
        if self.cleaned_data.get("role") == self.ROLE_ADMIN:
            # is_staff lets them into /admin/, is_superuser grants all permissions.
            user.is_staff = True
            user.is_superuser = True
        if commit:
            user.save()
        return user


class UserInfoForm(forms.ModelForm):
    """Edits the built-in User's personal details (used on the profile page)."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }


class CustomerProfileForm(forms.ModelForm):
    """Edits the CustomerProfile (phone, address, picture)."""

    class Meta:
        model = CustomerProfile
        fields = ["phone", "address", "profile_pic"]
        widgets = {
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "profile_pic": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),
        }


class StyledSetPasswordForm(SetPasswordForm):
    """Change password with just new password + confirmation (no old one).

    SetPasswordForm already provides 'new_password1' and 'new_password2' and
    runs Django's password validators; we only add Bootstrap styling here.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class MenuItemForm(forms.ModelForm):
    """Create/edit a menu item. Used by the admin's add and edit pages."""

    class Meta:
        model = MenuItem
        # The exact model fields shown on the form (in order).
        fields = ["category", "name", "description", "price", "image", "is_available"]
        # Each widget sets the HTML input type plus Bootstrap classes.
        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "is_available": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }
