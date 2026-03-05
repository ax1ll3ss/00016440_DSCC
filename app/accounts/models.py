from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """Extended user profile with anonymous display settings."""

    EMOJI_CHOICES = [
        ("😎", "Cool"),
        ("🦊", "Fox"),
        ("🐱", "Cat"),
        ("🌸", "Flower"),
        ("🔥", "Fire"),
        ("💀", "Skull"),
        ("👻", "Ghost"),
        ("🎭", "Mask"),
        ("🌙", "Moon"),
        ("⚡", "Lightning"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField(
        max_length=50,
        blank=True,
        help_text="Anonymous display name",
    )
    avatar_emoji = models.CharField(
        max_length=4,
        choices=EMOJI_CHOICES,
        default="👻",
    )
    bio = models.TextField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name or self.user.username

    def get_display_name(self):
        return self.display_name or f"Anonymous #{self.user.pk}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
