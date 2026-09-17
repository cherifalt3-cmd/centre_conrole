from rest_framework import serializers
from .models import Source, Article


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ['id', 'name', 'url', 'category']


class ArticleSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)
    source_category = serializers.CharField(source='source.category', read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'link', 'summary', 'severity', 'published_at', 'fetched_at',
            'source', 'source_name', 'source_category',
        ]
