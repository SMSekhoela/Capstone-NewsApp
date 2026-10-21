from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core import mail
from .models import Article


@receiver(post_save, sender=Article)
def handle_article_approval(sender, instance, created, **kwargs):
    """Notify subscribers and external services when an article is approved."""
    if instance.approved:
        recipients = set()

        for subscriber in instance.author.journalist_subscribers.all():
            if subscriber.email:
                recipients.add(subscriber.email)

        if instance.publisher:
            for subscriber in instance.publisher.publisher_subscribers.all():
                if subscriber.email:
                    recipients.add(subscriber.email)

        if recipients:
            subject = f"New Article: {instance.title}"
            message = f"Read the new article by {instance.author.username}:\n\n{instance.content[:200]}..."
            datatuple = [(subject, message, 'noreply@newsapp.com', [email]) for email in recipients]
            mail.send_mass_mail(datatuple, fail_silently=True)

        tweet_text = f"New Article Published! '{instance.title}' by {instance.author.username}."
        try:
            from Tweet.functions.tweet import Tweet
            Tweet().make_tweet(tweet_text)
        except ImportError:
            pass
        except Exception as e:
            print(f"X Notification Notice: {e}")
