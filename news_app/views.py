"""Views for the news application.

This module defines the request handlers for authentication, article management,
subscriptions, dashboards, and newsletters.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm

from .models import Article, Publisher, Newsletter, CustomUser


# ---------------------------------------------------------
# 1. AUTHENTICATION & DASHBOARD VIEWS
# ---------------------------------------------------------

def user_login(request):
    """Log in a user and redirect them to the dashboard.

    :param request: The HTTP request object.
    :return: A rendered login page or a redirect to the dashboard.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'news_app/login.html', {'form': form})


def register(request):
    """Create a new account and sign the user in.

    :param request: The HTTP request object.
    :return: A rendered registration form or a redirect to the dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"Account created successfully! Welcome as a {user.get_role_display()}."
            )
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()

    return render(request, 'news_app/register.html', {'form': form})


@login_required
def user_logout(request):
    """Log the current user out and redirect to the login page.

    :param request: The HTTP request object.
    :return: A redirect to the login view.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('user_login')


@login_required
def dashboard(request):
    """Display the appropriate dashboard for the authenticated user.

    :param request: The HTTP request object.
    :return: A rendered dashboard page with role-specific content.
    """
    user = request.user
    context = {'role': user.role}

    if user.role == 'reader':
        context['articles'] = Article.objects.filter(approved=True).filter(
            publisher__in=user.subscribed_publishers.all()
        ) | Article.objects.filter(approved=True).filter(
            author__in=user.subscribed_journalists.all()
        )
        context['newsletters'] = Newsletter.objects.all()

    elif user.role == 'journalist':
        context['articles'] = Article.objects.filter(author=user)
        context['newsletters'] = Newsletter.objects.filter(author=user)

    elif user.role == 'editor':
        context['pending_articles'] = Article.objects.filter(approved=False)
        context['approved_articles'] = Article.objects.filter(approved=True)

    return render(request, 'news_app/dashboard.html', context)


# ---------------------------------------------------------
# 2. ARTICLE VIEWS (Journalists & Readers)
# ---------------------------------------------------------

@login_required(login_url='user_login')
def article_list(request):
    """Show the list of approved articles for authenticated users.

    :param request: The HTTP request object.
    :return: A rendered article list page.
    """
    articles = Article.objects.filter(approved=True).order_by('-created_at')
    return render(request, 'news_app/article_list.html', {'articles': articles})


@login_required(login_url='user_login')
def article_detail(request, pk):
    """Display one article while protecting unapproved content.

    :param request: The HTTP request object.
    :param pk: The primary key of the article.
    :return: A rendered article detail page.
    """
    article = get_object_or_404(Article, pk=pk)
    if not article.approved and (not request.user.is_authenticated or request.user.role == 'reader'):
        raise PermissionDenied("This article has not been approved yet.")
    return render(request, 'news_app/article_detail.html', {'article': article})


@login_required
def create_article(request):
    """Allow journalists to create and submit an article for review.

    :param request: The HTTP request object.
    :return: A redirect to the dashboard or a rendered article form.
    """
    if request.user.role != 'journalist':
        raise PermissionDenied("Only journalists can create articles.")

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        publisher_id = request.POST.get('publisher')

        if title and content:
            publisher = Publisher.objects.filter(id=publisher_id).first() if publisher_id else None
            Article.objects.create(
                title=title,
                content=content,
                author=request.user,
                publisher=publisher,
                approved=False
            )
            messages.success(request, "Article submitted successfully! Awaiting editor approval.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please fill in all required fields.")

    publishers = Publisher.objects.all()
    return render(request, 'news_app/create_article.html', {'publishers': publishers})


# ---------------------------------------------------------
# 3. EDITOR APPROVAL & MANAGEMENT VIEWS
# ---------------------------------------------------------

@login_required
def approve_article(request, pk):
    """Approve an article and notify subscribers.

    :param request: The HTTP request object.
    :param pk: The primary key of the article.
    :return: A redirect to the dashboard.
    """
    if request.user.role != 'editor':
        raise PermissionDenied("Only editors can approve articles.")

    article = get_object_or_404(Article, pk=pk)
    article.approved = True
    article.save()

    messages.success(request, f"Article '{article.title}' has been approved, emailed to subscribers, and shared to X!")
    return redirect('dashboard')


@login_required
def delete_article(request, pk):
    """Delete an article if the user is allowed to do so.

    :param request: The HTTP request object.
    :param pk: The primary key of the article.
    :return: A redirect to the dashboard.
    """
    article = get_object_or_404(Article, pk=pk)

    if request.user.role != 'editor' and article.author != request.user:
        raise PermissionDenied("You do not have permission to delete this article.")

    article.delete()
    messages.success(request, "Article deleted successfully.")
    return redirect('dashboard')


# ---------------------------------------------------------
# 4. SUBSCRIPTION MANAGEMENT VIEWS (Readers)
# ---------------------------------------------------------

@login_required
def toggle_publisher_subscription(request, publisher_id):
    """Toggle a reader subscription to a publisher.

    :param request: The HTTP request object.
    :param publisher_id: The publisher identifier.
    :return: A redirect to the dashboard.
    """
    if request.user.role != 'reader':
        raise PermissionDenied("Only readers can manage subscriptions.")

    publisher = get_object_or_404(Publisher, id=publisher_id)
    if publisher in request.user.subscribed_publishers.all():
        request.user.subscribed_publishers.remove(publisher)
        messages.info(request, f"Unsubscribed from {publisher.name}.")
    else:
        request.user.subscribed_publishers.add(publisher)
        messages.success(request, f"Subscribed to {publisher.name}!")

    return redirect('dashboard')


@login_required
def toggle_journalist_subscription(request, journalist_id):
    """Toggle a reader subscription to a journalist.

    :param request: The HTTP request object.
    :param journalist_id: The journalist identifier.
    :return: A redirect to the dashboard.
    """
    if request.user.role != 'reader':
        raise PermissionDenied("Only readers can manage subscriptions.")

    journalist = get_object_or_404(CustomUser, id=journalist_id, role='journalist')
    if journalist in request.user.subscribed_journalists.all():
        request.user.subscribed_journalists.remove(journalist)
        messages.info(request, f"Unsubscribed from {journalist.username}.")
    else:
        request.user.subscribed_journalists.add(journalist)
        messages.success(request, f"Subscribed to {journalist.username}!")

    return redirect('dashboard')


# ---------------------------------------------------------
# 5. NEWSLETTER VIEWS
# ---------------------------------------------------------

@login_required
def newsletter_list(request):
    """List newsletters in reverse chronological order.

    :param request: The HTTP request object.
    :return: A rendered newsletter list page.
    """
    newsletters = Newsletter.objects.all().order_by('-created_at')
    return render(request, 'news_app/newsletter_list.html', {'newsletters': newsletters})


@login_required
def create_newsletter(request):
    """Create a newsletter from approved articles.

    :param request: The HTTP request object.
    :return: A redirect to the dashboard or a rendered newsletter form.
    """
    if request.user.role not in ['journalist', 'editor']:
        raise PermissionDenied("Only journalists and editors can create newsletters.")

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        article_ids = request.POST.getlist('articles')

        if title and description:
            newsletter = Newsletter.objects.create(
                title=title,
                description=description,
                author=request.user
            )
            if article_ids:
                newsletter.articles.set(Article.objects.filter(id__in=article_ids))
            messages.success(request, "Newsletter created successfully!")
            return redirect('dashboard')

    articles = Article.objects.filter(approved=True)
    return render(request, 'news_app/create_newsletter.html', {'articles': articles})
