from rest_framework import serializers
from .models import CustomUser, Publisher, Article, Newsletter


class CustomUserSerializer(serializers.ModelSerializer):
    """Serialize basic user data for API responses."""

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role']


class PublisherSerializer(serializers.ModelSerializer):
    """Serialize publisher details for the API."""

    class Meta:
        model = Publisher
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    """Serialize article objects, exposing the author username as read-only."""

    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author', 'publisher', 'created_at', 'approved']


class NewsletterSerializer(serializers.ModelSerializer):
    """Serialize newsletter data including related article information."""

    class Meta:
        model = Newsletter
        fields = '__all__'
