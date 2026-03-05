from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify


class Tag(models.Model):
    """Category tags for confessions."""

    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Confession(models.Model):
    """An anonymous confession post."""

    MOOD_CHOICES = [
        ("happy", "😊 Happy"),
        ("sad", "😢 Sad"),
        ("angry", "😡 Angry"),
        ("anxious", "😰 Anxious"),
        ("relieved", "😌 Relieved"),
        ("guilty", "😔 Guilty"),
        ("excited", "🤩 Excited"),
        ("confused", "😵 Confused"),
    ]

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="confessions",
    )
    title = models.CharField(max_length=200)
    content = models.TextField(max_length=5000)
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, default="happy")
    is_anonymous = models.BooleanField(
        default=True,
        help_text="Post anonymously",
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="confessions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("confession_detail", kwargs={"pk": self.pk})

    def get_author_display(self):
        if self.is_anonymous:
            return f"Anonymous #{self.author.pk}"
        return self.author.profile.get_display_name()

    def get_mood_emoji(self):
        mood_map = dict(self.MOOD_CHOICES)
        return mood_map.get(self.mood, "")

    @property
    def reaction_summary(self):
        """Return a dict of reaction types and their counts."""
        reactions = self.reactions.values("reaction_type").annotate(
            count=models.Count("id")
        )
        return {r["reaction_type"]: r["count"] for r in reactions}


class Comment(models.Model):
    """A comment on a confession."""

    confession = models.ForeignKey(
        Confession,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    content = models.TextField(max_length=1000)
    is_anonymous = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.get_author_display()} on {self.confession.title}"

    def get_author_display(self):
        if self.is_anonymous:
            return f"Anonymous #{self.author.pk}"
        return self.author.profile.get_display_name()


class Reaction(models.Model):
    """A reaction (emoji) on a confession."""

    REACTION_CHOICES = [
        ("heart", "❤️"),
        ("thumbsup", "👍"),
        ("cry", "😢"),
        ("angry", "😡"),
        ("fire", "🔥"),
    ]

    confession = models.ForeignKey(
        Confession,
        on_delete=models.CASCADE,
        related_name="reactions",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reactions",
    )
    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("confession", "user", "reaction_type")

    def __str__(self):
        return f"{self.get_reaction_type_display()} on {self.confession.title}"
