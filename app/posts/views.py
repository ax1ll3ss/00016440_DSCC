from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Count, Q

from .models import Confession, Comment, Reaction, Tag
from .forms import ConfessionForm, CommentForm


def home_view(request):
    """Home page with paginated confession feed."""
    confessions = Confession.objects.select_related("author__profile").prefetch_related(
        "tags", "comments", "reactions"
    )

    # Filter by tag
    tag_slug = request.GET.get("tag")
    if tag_slug:
        confessions = confessions.filter(tags__slug=tag_slug)

    # Filter by mood
    mood = request.GET.get("mood")
    if mood:
        confessions = confessions.filter(mood=mood)

    # Search
    query = request.GET.get("q")
    if query:
        confessions = confessions.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    paginator = Paginator(confessions, 10)
    page = request.GET.get("page")
    confessions_page = paginator.get_page(page)

    tags = Tag.objects.annotate(count=Count("confessions")).order_by("-count")[:10]

    context = {
        "confessions": confessions_page,
        "tags": tags,
        "current_tag": tag_slug,
        "current_mood": mood,
        "query": query or "",
        "mood_choices": Confession.MOOD_CHOICES,
    }
    return render(request, "posts/home.html", context)


@login_required
def confession_create_view(request):
    """Create a new confession."""
    if request.method == "POST":
        form = ConfessionForm(request.POST)
        if form.is_valid():
            confession = form.save(commit=False)
            confession.author = request.user
            confession.save()
            form.save_m2m()  # Save tags M2M relationship
            messages.success(request, "Your confession has been shared! 🎭")
            return redirect("home")
    else:
        form = ConfessionForm()

    return render(request, "posts/confession_form.html", {
        "form": form,
        "title": "Share a Confession",
    })


def confession_detail_view(request, pk):
    """View a single confession with comments and reactions."""
    confession = get_object_or_404(
        Confession.objects.select_related("author__profile").prefetch_related(
            "tags", "comments__author__profile", "reactions"
        ),
        pk=pk,
    )
    comment_form = CommentForm()

    # Get user's existing reactions
    user_reactions = []
    if request.user.is_authenticated:
        user_reactions = list(
            confession.reactions.filter(user=request.user).values_list(
                "reaction_type", flat=True
            )
        )

    # Pre-compute reaction counts for each type
    reaction_summary = confession.reaction_summary
    reaction_data = []
    for rtype, emoji in Reaction.REACTION_CHOICES:
        reaction_data.append({
            "type": rtype,
            "emoji": emoji,
            "count": reaction_summary.get(rtype, 0),
            "active": rtype in user_reactions,
        })

    context = {
        "confession": confession,
        "comment_form": comment_form,
        "user_reactions": user_reactions,
        "reaction_data": reaction_data,
    }
    return render(request, "posts/confession_detail.html", context)


@login_required
def confession_edit_view(request, pk):
    """Edit an existing confession (owner only)."""
    confession = get_object_or_404(Confession, pk=pk, author=request.user)

    if request.method == "POST":
        form = ConfessionForm(request.POST, instance=confession)
        if form.is_valid():
            form.save()
            messages.success(request, "Confession updated! ✏️")
            return redirect("confession_detail", pk=pk)
    else:
        form = ConfessionForm(instance=confession)

    return render(request, "posts/confession_form.html", {
        "form": form,
        "title": "Edit Confession",
        "editing": True,
    })


@login_required
def confession_delete_view(request, pk):
    """Delete a confession (owner only)."""
    confession = get_object_or_404(Confession, pk=pk, author=request.user)

    if request.method == "POST":
        confession.delete()
        messages.success(request, "Confession deleted. 🗑️")
        return redirect("home")

    return render(request, "posts/confession_confirm_delete.html", {
        "confession": confession,
    })


@login_required
def comment_add_view(request, pk):
    """Add a comment to a confession."""
    confession = get_object_or_404(Confession, pk=pk)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.confession = confession
            comment.save()
            messages.success(request, "Comment added! 💬")

    return redirect("confession_detail", pk=pk)


@login_required
def reaction_toggle_view(request, pk, reaction_type):
    """Toggle a reaction on a confession (AJAX-friendly)."""
    confession = get_object_or_404(Confession, pk=pk)

    valid_types = [r[0] for r in Reaction.REACTION_CHOICES]
    if reaction_type not in valid_types:
        return JsonResponse({"error": "Invalid reaction type"}, status=400)

    reaction, created = Reaction.objects.get_or_create(
        confession=confession,
        user=request.user,
        reaction_type=reaction_type,
    )

    if not created:
        reaction.delete()
        action = "removed"
    else:
        action = "added"

    count = confession.reactions.filter(reaction_type=reaction_type).count()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "action": action,
            "count": count,
            "reaction_type": reaction_type,
        })

    return redirect("confession_detail", pk=pk)


def dashboard_view(request):
    """Dashboard with stats and analytics."""
    total_confessions = Confession.objects.count()
    total_comments = Comment.objects.count()
    total_reactions = Reaction.objects.count()

    popular_tags = Tag.objects.annotate(
        count=Count("confessions")
    ).order_by("-count")[:5]

    mood_choices_map = dict(Confession.MOOD_CHOICES)
    mood_stats_qs = (
        Confession.objects.values("mood")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    # Pre-compute display values to avoid template errors
    mood_stats = []
    for stat in mood_stats_qs:
        percentage = (
            round(stat["count"] / total_confessions * 100)
            if total_confessions > 0
            else 0
        )
        mood_stats.append({
            "mood": stat["mood"],
            "mood_display": mood_choices_map.get(stat["mood"], stat["mood"]),
            "count": stat["count"],
            "percentage": percentage,
        })

    recent_confessions = Confession.objects.select_related(
        "author__profile"
    ).prefetch_related("comments", "reactions")[:5]

    context = {
        "total_confessions": total_confessions,
        "total_comments": total_comments,
        "total_reactions": total_reactions,
        "popular_tags": popular_tags,
        "mood_stats": mood_stats,
        "recent_confessions": recent_confessions,
    }
    return render(request, "posts/dashboard.html", context)
