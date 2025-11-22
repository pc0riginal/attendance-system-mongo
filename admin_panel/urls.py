from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('create-user/', views.create_user, name='admin_create_user'),
    path('edit-user/<str:user_id>/', views.edit_user, name='admin_edit_user'),
    path('delete-user/<str:user_id>/', views.delete_user, name='admin_delete_user'),
]