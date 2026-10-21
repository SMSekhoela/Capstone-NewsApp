from django.db import models
from django.contrib.auth.models import AbstractUser, Group


class CustomUser(AbstractUser):
    """Custom user model that supports readers, journalists, and editors."""

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
        """Save the user and ensure role-based group assignment and subscriptions remain valid."""
        if self.role == 'journalist':
            super().save(*args, **kwargs)
            self.subscribed_publishers.clear()
            self.subscribed_journalists.clear()
        else:
            super().save(*args, **kwargs)

        group, _ = Group.objects.get_or_create(name=self.role.capitalize())
        self.groups.add(group)


class Publisher(models.Model):
    """Represents a news publisher that can have assigned editors and journalists."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    editors = models.ManyToManyField(
        CustomUser, related_name='editing_publishers', limit_choices_to={'role': 'editor'}
    )
    journalists = models.ManyToManyField(
        CustomUser, related_name='writing_publishers', limit_choices_to={'role': 'journalist'}
    )

    def __str__(self):
        """Return a readable publisher name."""
        return self.name


class Article(models.Model):
    """Stores published or pending news content submitted by journalists."""

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
        """Return the article title for display in the admin and shell."""
        return self.title


class Newsletter(models.Model):
    """Represents a curated collection of approved articles created by a user."""

    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='newsletters'
    )
    articles = models.ManyToManyField(Article, related_name='newsletters')

    def __str__(self):
        """Return the newsletter title."""
        return self.title
