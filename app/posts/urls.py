from django.urls import path

from . import views

urlpatterns = [
    path("new/", views.confession_create_view, name="confession_create"),
    path("<int:pk>/", views.confession_detail_view, name="confession_detail"),
    path("<int:pk>/edit/", views.confession_edit_view, name="confession_edit"),
    path("<int:pk>/delete/", views.confession_delete_view, name="confession_delete"),
    path("<int:pk>/comment/", views.comment_add_view, name="comment_add"),
    path(
        "<int:pk>/react/<str:reaction_type>/",
        views.reaction_toggle_view,
        name="reaction_toggle",
    ),
]
