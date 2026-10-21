"""Database models for the news application.

This module defines the user roles, publishers, articles, and newsletters used by
the application.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser, Group


class CustomUser(AbstractUser):
    """Represent a user with a role in the news platform.

    :param AbstractUser: Base Django user model.
    :return: A custom user instance for a reader, journalist, or editor.
    """

    ROLE_CHOICES = (
        ('reader', 'Reader'),
        ('journalist', 'Journalist'),
        ('editor', 'Editor'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='reader')

    # Reader-specific subscriptions
    subscribed_publishers = models.ManyToManyField(
        'Publisher', blank=True, related_name='publisher_subscribers'
    )
    subscribed_journalists = models.ManyToManyField(
        'self', blank=True, symmetrical=False, related_name='journalist_subscribers'
    )

    def save(self, *args, **kwargs):
        """Save the user and keep the role-based group assignment consistent.

        :param args: Positional arguments for the parent save method.
        :param kwargs: Keyword arguments for the parent save method.
        :return: None
        """
        if self.role == 'journalist':
            super().save(*args, **kwargs)
            self.subscribed_publishers.clear()
            self.subscribed_journalists.clear()
        else:
            super().save(*args, **kwargs)

        group, _ = Group.objects.get_or_create(name=self.role.capitalize())
        self.groups.add(group)


class Publisher(models.Model):
    """Represent a news publisher with assigned editors and journalists.

    :param models.Model: Django base model class.
    :return: A publisher instance.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    editors = models.ManyToManyField(
        CustomUser, related_name='editing_publishers', limit_choices_to={'role': 'editor'}
    )
    journalists = models.ManyToManyField(
        CustomUser, related_name='writing_publishers', limit_choices_to={'role': 'journalist'}
    )

    def __str__(self):
        """Return the publisher name for display.

        :return: The publisher's name.
        """
        return self.name


class Article(models.Model):
    """Store a news article submitted by a journalist.

    :param models.Model: Django base model class.
    :return: An article instance.
    """

    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='articles', limit_choices_to={'role': 'journalist'}
    )
    publisher = models.ForeignKey(
        Publisher, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        """Return the article title for readable display.

        :return: The article title.
        """
        return self.title


class Newsletter(models.Model):
    """Represent a curated collection of approved articles.

    :param models.Model: Django base model class.
    :return: A newsletter instance.
    """

    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='newsletters'
    )
    articles = models.ManyToManyField(Article, related_name='newsletters')

    def __str__(self):
        """Return the newsletter title.

        :return: The newsletter title.
        """
        return self.title
