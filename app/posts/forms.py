from django import forms

from .models import Confession, Comment


class ConfessionForm(forms.ModelForm):
    """Form for creating/editing confessions."""

    class Meta:
        model = Confession
        fields = ["title", "content", "mood", "is_anonymous", "tags"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Give your confession a title...",
            }),
            "content": forms.Textarea(attrs={
                "class": "form-input",
                "rows": 6,
                "placeholder": "Share what's on your mind...",
            }),
            "mood": forms.Select(attrs={"class": "form-input"}),
            "is_anonymous": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
            "tags": forms.CheckboxSelectMultiple(),
        }


class CommentForm(forms.ModelForm):
    """Form for adding comments."""

    class Meta:
        model = Comment
        fields = ["content", "is_anonymous"]
        widgets = {
            "content": forms.Textarea(attrs={
                "class": "form-input",
                "rows": 3,
                "placeholder": "Write a supportive comment...",
            }),
            "is_anonymous": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        }
