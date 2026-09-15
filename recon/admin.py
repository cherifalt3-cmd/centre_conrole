from django.contrib import admin
from .models import (
    Target, Tool, ToolOption, ToolOptionChoice, Catalog, CatalogEntry,
)


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'date_added')
    search_fields = ('name', 'address')


class ToolOptionInline(admin.TabularInline):
    model = ToolOption
    extra = 1


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_command', 'phase')
    list_filter = ('phase',)
    inlines = [ToolOptionInline]


class ToolOptionChoiceInline(admin.TabularInline):
    model = ToolOptionChoice
    extra = 1


@admin.register(ToolOption)
class ToolOptionAdmin(admin.ModelAdmin):
    list_display = ('label', 'tool', 'option_type', 'flag')
    list_filter = ('tool', 'option_type')
    inlines = [ToolOptionChoiceInline]


class CatalogEntryInline(admin.TabularInline):
    model = CatalogEntry
    extra = 1


@admin.register(Catalog)
class CatalogAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [CatalogEntryInline]
