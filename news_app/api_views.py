from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import models
from .models import Article
from .serializers import ArticleSerializer


class IsJournalist(permissions.BasePermission):
    """Allow only authenticated journalists to access a protected endpoint."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'journalist'


class IsEditor(permissions.BasePermission):
    """Allow only authenticated editors to access an editorial endpoint."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'editor'


class ArticleListAPIView(generics.ListAPIView):
    """Return all approved articles for public viewing."""

    queryset = Article.objects.filter(approved=True)
    serializer_class = ArticleSerializer
    permission_classes = [permissions.AllowAny]


class SubscribedArticlesAPIView(APIView):
    """Return articles matching the authenticated reader's subscriptions."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Fetch approved content from subscribed publishers or journalists."""
        user = request.user
        articles = Article.objects.filter(
            approved=True
        ).filter(
            models.Q(publisher__in=user.subscribed_publishers.all()) |
            models.Q(author__in=user.subscribed_journalists.all())
        ).distinct()

        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ArticleCreateAPIView(generics.CreateAPIView):
    """Create a new article for an authenticated journalist."""

    serializer_class = ArticleSerializer
    permission_classes = [IsJournalist]

    def perform_create(self, serializer):
        """Attach the current user as the article's author before saving."""
        serializer.save(author=self.request.user)


class ArticleDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a single article by ID."""

    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def get_permissions(self):
        """Allow public reads but restrict writes to editors or journalists."""
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [IsEditor() | IsJournalist()]
