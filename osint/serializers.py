from rest_framework import serializers
from .models import Search


class SearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Search
        fields = ['id', 'query', 'query_type', 'status', 'results', 'error_message', 'created_at']
        read_only_fields = ['status', 'results', 'error_message']
