from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.cheese_list, name="cheese_list"),
    path("cheese/<int:cheese_id>/", views.cheese_detail, name="cheese_detail"),
    path("cheese/add/", views.cheese_create, name="cheese_create"),
    path("cheese/<int:cheese_id>/edit/",
         views.cheese_edit, name="cheese_edit"),
    path("cheese/<int:cheese_id>/delete/",
         views.cheese_delete, name="cheese_delete"),
    path("about/", views.about, name="about"),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="catalog/login.html"),
        name="login",
    ),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(next_page="/"), name="logout"
    ),
    path("batches/", views.batch_list, name="batch_list"),
    path("batches/create/", views.batch_create, name="batch_create"),
    path("batches/<int:batch_id>/", views.batch_detail, name="batch_detail"),
    path(
        "batches/<int:batch_id>/add_item/",
        views.batch_add_item, name="batch_add_item"
    ),
    path(
        "batch_item/<int:item_id>/edit/",
        views.batch_item_edit, name="batch_item_edit"
    ),
    path(
        "batch_item/<int:item_id>/delete/",
        views.batch_item_delete,
        name="batch_item_delete",
    ),
    path("batches/<int:batch_id>/delete/",
         views.batch_delete, name="batch_delete"),
]
