from django.contrib import admin
from .models import Target


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'date_added')
    search_fields = ('name', 'address')
