from django.contrib import admin

from .models import Confession, Comment, Reaction, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ("author", "created_at")


class ReactionInline(admin.TabularInline):
    model = Reaction
    extra = 0
    readonly_fields = ("user", "reaction_type", "created_at")


@admin.register(Confession)
class ConfessionAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "mood", "is_anonymous", "created_at")
    list_filter = ("mood", "is_anonymous", "created_at", "tags")
    search_fields = ("title", "content")
    filter_horizontal = ("tags",)
    inlines = [CommentInline, ReactionInline]
    readonly_fields = ("created_at", "updated_at")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("confession", "author", "is_anonymous", "created_at")
    list_filter = ("is_anonymous", "created_at")
    search_fields = ("content",)


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ("confession", "user", "reaction_type", "created_at")
    list_filter = ("reaction_type",)
