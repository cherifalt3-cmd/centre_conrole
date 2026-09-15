from rest_framework import serializers
from .models import Target


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ['id', 'name', 'address', 'date_added', 'notes']
