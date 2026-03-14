from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import Profile


class UserRegisterForm(UserCreationForm):
    """Registration form with email field."""

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-input"
            field.widget.attrs["placeholder"] = field.label


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile."""

    class Meta:
        model = Profile
        fields = ["display_name", "avatar_emoji", "bio"]
        widgets = {
            "display_name": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Anonymous display name",
            }),
            "avatar_emoji": forms.Select(attrs={"class": "form-input"}),
            "bio": forms.Textarea(attrs={
                "class": "form-input",
                "rows": 3,
                "placeholder": "Tell us about yourself...",
            }),
        }


class UserLoginForm(AuthenticationForm):
    """Login form with styled fields."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-input"
            field.widget.attrs["placeholder"] = field.label
