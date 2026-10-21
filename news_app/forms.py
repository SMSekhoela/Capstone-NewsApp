from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Custom registration form that includes the user's selected platform role."""

    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Select your account role on the platform."
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role']
