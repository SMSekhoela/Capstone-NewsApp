from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from . import views, api_views

urlpatterns = [
    # Web UI Routes
    path('', views.article_list, name='article_list'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='news_app/password_reset_form.html',
        email_template_name='news_app/password_reset_email.html',
        success_url=reverse_lazy('password_reset_done')
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='news_app/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='news_app/password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete')
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='news_app/password_reset_complete.html'
    ), name='password_reset_complete'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('article/<int:pk>/', views.article_detail, name='article_detail'),
    path('article/create/', views.create_article, name='create_article'),
    path('article/<int:pk>/approve/', views.approve_article, name='approve_article'),
    path('article/<int:pk>/delete/', views.delete_article, name='delete_article'),

    # Subscriptions
    path('subscribe/publisher/<int:publisher_id>/', views.toggle_publisher_subscription, name='toggle_publisher_sub'),
    path('subscribe/journalist/<int:journalist_id>/', views.toggle_journalist_subscription, name='toggle_journalist_sub'),

    # Newsletters
    path('newsletters/', views.newsletter_list, name='newsletter_list'),
    path('newsletters/create/', views.create_newsletter, name='create_newsletter'),

    # REST API Routes
    path('api/articles/', api_views.ArticleListAPIView.as_view(), name='api_articles_list'),
    path('api/articles/subscribed/', api_views.SubscribedArticlesAPIView.as_view(), name='api_articles_subscribed'),
    path('api/articles/create/', api_views.ArticleCreateAPIView.as_view(), name='api_article_create'),
    path('api/articles/<int:pk>/', api_views.ArticleDetailAPIView.as_view(), name='api_article_detail'),
]
