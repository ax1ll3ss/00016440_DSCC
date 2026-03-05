import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from posts.models import Confession, Comment, Reaction


@pytest.mark.django_db
class TestHomePage(TestCase):
    """Test that the home page loads correctly."""

    def test_home_page_returns_200(self):
        client = Client()
        response = client.get(reverse("home"))
        assert response.status_code == 200

    def test_home_contains_title(self):
        client = Client()
        response = client.get(reverse("home"))
        assert b"Confessions" in response.content


@pytest.mark.django_db
class TestUserRegistration(TestCase):
    """Test user registration flow."""

    def test_register_page_loads(self):
        client = Client()
        response = client.get(reverse("register"))
        assert response.status_code == 200

    def test_register_creates_user(self):
        client = Client()
        response = client.post(reverse("register"), {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        })
        assert response.status_code == 302  # Redirect after success
        assert User.objects.filter(username="testuser").exists()


@pytest.mark.django_db
class TestConfessionCRUD(TestCase):
    """Test confession CRUD operations."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )
        self.client = Client()
        self.client.login(username="testuser", password="testpass123")
        self.confession = Confession.objects.create(
            author=self.user,
            title="Test Confession",
            content="This is a test confession.",
            mood="happy",
        )

    def test_create_confession(self):
        response = self.client.post(reverse("confession_create"), {
            "title": "New Confession",
            "content": "Something new",
            "mood": "sad",
            "is_anonymous": True,
        })
        assert response.status_code == 302
        assert Confession.objects.filter(title="New Confession").exists()

    def test_confession_detail_page(self):
        response = self.client.get(
            reverse("confession_detail", kwargs={"pk": self.confession.pk})
        )
        assert response.status_code == 200
        assert b"Test Confession" in response.content

    def test_edit_confession(self):
        response = self.client.post(
            reverse("confession_edit", kwargs={"pk": self.confession.pk}),
            {
                "title": "Updated Title",
                "content": "Updated content",
                "mood": "relieved",
                "is_anonymous": True,
            },
        )
        assert response.status_code == 302
        self.confession.refresh_from_db()
        assert self.confession.title == "Updated Title"

    def test_delete_confession(self):
        response = self.client.post(
            reverse("confession_delete", kwargs={"pk": self.confession.pk})
        )
        assert response.status_code == 302
        assert not Confession.objects.filter(pk=self.confession.pk).exists()


@pytest.mark.django_db
class TestComments(TestCase):
    """Test comment functionality."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )
        self.client = Client()
        self.client.login(username="testuser", password="testpass123")
        self.confession = Confession.objects.create(
            author=self.user,
            title="Confession for Comments",
            content="Content here",
            mood="happy",
        )

    def test_add_comment(self):
        response = self.client.post(
            reverse("comment_add", kwargs={"pk": self.confession.pk}),
            {
                "content": "A supportive comment",
                "is_anonymous": True,
            },
        )
        assert response.status_code == 302
        assert Comment.objects.filter(confession=self.confession).count() == 1


@pytest.mark.django_db
class TestReactions(TestCase):
    """Test reaction functionality."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )
        self.client = Client()
        self.client.login(username="testuser", password="testpass123")
        self.confession = Confession.objects.create(
            author=self.user,
            title="Confession for Reactions",
            content="Content here",
            mood="happy",
        )

    def test_add_reaction(self):
        response = self.client.get(
            reverse("reaction_toggle", kwargs={
                "pk": self.confession.pk,
                "reaction_type": "heart",
            })
        )
        assert response.status_code == 302
        assert Reaction.objects.filter(
            confession=self.confession, user=self.user, reaction_type="heart"
        ).exists()

    def test_toggle_reaction_removes(self):
        # Add reaction
        Reaction.objects.create(
            confession=self.confession,
            user=self.user,
            reaction_type="heart",
        )
        # Toggle (remove)
        self.client.get(
            reverse("reaction_toggle", kwargs={
                "pk": self.confession.pk,
                "reaction_type": "heart",
            })
        )
        assert not Reaction.objects.filter(
            confession=self.confession, user=self.user, reaction_type="heart"
        ).exists()


@pytest.mark.django_db
class TestDashboard(TestCase):
    """Test dashboard view."""

    def test_dashboard_loads(self):
        client = Client()
        response = client.get(reverse("dashboard"))
        assert response.status_code == 200
        assert b"Dashboard" in response.content
