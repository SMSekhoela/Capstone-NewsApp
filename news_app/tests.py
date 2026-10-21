from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from .models import CustomUser, Article, Publisher


class NewsAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.reader = CustomUser.objects.create_user(
            username='reader',
            email='reader@example.com',
            password='password123',
            role='reader'
        )
        self.journalist = CustomUser.objects.create_user(username='journo', password='password123', role='journalist')
        self.editor = CustomUser.objects.create_user(username='editor', password='password123', role='editor')

        self.publisher = Publisher.objects.create(name='Global News')
        self.article = Article.objects.create(
            title='Breaking Tech',
            content='AI updates...',
            author=self.journalist,
            publisher=self.publisher,
            approved=False
        )

    def test_reader_cannot_create_article(self):
        self.client.force_authenticate(user=self.reader)
        response = self.client.post(reverse('api_article_create'), {'title': 'Invalid', 'content': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_journalist_can_create_article(self):
        self.client.force_authenticate(user=self.journalist)
        response = self.client.post(reverse('api_article_create'), {'title': 'Valid Title', 'content': 'Valid Body'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_subscribed_articles_endpoint(self):
        self.reader.subscribed_publishers.add(self.publisher)
        self.article.approved = True
        self.article.save()

        self.client.force_authenticate(user=self.reader)
        response = self.client.get(reverse('api_articles_subscribed'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_article_list_requires_login(self):
        response = self.client.get(reverse('article_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/?next=', response.headers['Location'])

    @patch('Tweet.functions.tweet.Tweet.make_tweet')
    @patch('django.core.mail.send_mass_mail')
    def test_article_approval_triggers_signal(self, mock_email, mock_tweet):
        self.reader.subscribed_publishers.add(self.publisher)

        # Approve triggers signal
        self.article.approved = True
        self.article.save()

        self.assertTrue(mock_email.called)
        self.assertTrue(mock_tweet.called)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_password_reset_flow(self):
        user = CustomUser.objects.create_user(
            username='resetuser',
            email='resetuser@example.com',
            password='old-password-123',
            role='reader'
        )

        response = self.client.post(reverse('password_reset'), {'email': 'resetuser@example.com'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('resetuser@example.com', mail.outbox[0].to)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        confirm_url = reverse('password_reset_confirm', args=[uid, token])

        response = self.client.get(confirm_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], f"/reset/{uid}/set-password/")

        set_password_url = reverse('password_reset_confirm', args=[uid, token])
        set_password_url = set_password_url.replace(f'/{token}/', '/set-password/')

        response = self.client.post(set_password_url, {
            'new_password1': 'new-password-456',
            'new_password2': 'new-password-456',
        })
        self.assertRedirects(response, reverse('password_reset_complete'))

        user.refresh_from_db()
        self.assertTrue(user.check_password('new-password-456'))
