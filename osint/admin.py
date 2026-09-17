from django.contrib import admin
from .models import Search


@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    list_display = ('query', 'query_type', 'status', 'job_key', 'error_message', 'created_at')
    list_filter = ('query_type', 'status')
