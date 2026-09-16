from rest_framework import serializers
from .models import (
    Target, Tool, ToolOption, ToolOptionChoice, Catalog, CatalogEntry, CommandPreset,
)


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ['id', 'name', 'address', 'date_added', 'notes']


class ToolOptionChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolOptionChoice
        fields = ['id', 'value', 'label']


class CatalogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogEntry
        fields = ['id', 'value', 'description']


class CatalogSerializer(serializers.ModelSerializer):
    entries = CatalogEntrySerializer(many=True, read_only=True)

    class Meta:
        model = Catalog
        fields = ['id', 'name', 'entries']


class ToolOptionSerializer(serializers.ModelSerializer):
    choices = ToolOptionChoiceSerializer(many=True, read_only=True)
    catalog = CatalogSerializer(read_only=True)

    class Meta:
        model = ToolOption
        fields = ['id', 'label', 'group', 'flag', 'option_type', 'help_text', 'choices', 'catalog']


class ToolSerializer(serializers.ModelSerializer):
    options = ToolOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Tool
        fields = ['id', 'name', 'base_command', 'phase', 'description', 'options']


class CommandPresetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommandPreset
        fields = ['id', 'label', 'category', 'phase', 'template', 'order']
