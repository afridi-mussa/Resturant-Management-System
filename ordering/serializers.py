"""
Serializers for the REST API.

A serializer converts model instances (Python objects) into JSON for API
responses, and validates incoming JSON when creating/updating objects.
"""
from rest_framework import serializers

from .models import MenuItem


class MenuItemSerializer(serializers.ModelSerializer):
    """Turns a MenuItem into JSON (and back). Exposes every model field."""

    # Read-only extra field: pulls the related category's name so API consumers
    # get a human-readable category instead of only its numeric id.
    category_name = serializers.CharField(
        source="category.name", read_only=True
    )

    class Meta:
        model = MenuItem
        fields = "__all__"      # include all model fields (plus category_name above)
