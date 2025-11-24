from django.urls import path
from . import views_mongodb as views
from . import mandal_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Devotee URLs
    path('devotees/', views.devotee_list, name='devotee_list'),
    path('devotees/add/', views.devotee_add, name='devotee_add'),
    path('devotees/<str:pk>/', views.devotee_detail, name='devotee_detail'),
    path('devotees/edit/<str:pk>/', views.devotee_edit, name='devotee_edit'),
    
    # Sabha URLs
    path('sabhas/', views.sabha_list, name='sabha_list'),
    path('sabhas/add/', views.sabha_add, name='sabha_add'),
    path('sabhas/<str:sabha_id>/attendance/', views.mark_attendance, name='mark_attendance'),
    
    # Reports
    path('reports/', views.attendance_report, name='attendance_report'),
    path('reports/analytics/', views.attendance_analytics, name='attendance_analytics'),
    path('reports/export/', views.export_attendance, name='export_attendance'),
    
    # Upload
    path('upload-devotees/', views.upload_devotees, name='upload_devotees'),
    path('process-batch/', views.process_devotees_batch, name='process_devotees_batch'),
    path('cancel-batch/', views.cancel_batch_processing, name='cancel_batch_processing'),
    
    # API
    path('api/save-attendance/', views.save_individual_attendance, name='save_individual_attendance'),
    
    # Delete URLs
    path('devotees/delete/<str:pk>/', views.devotee_delete, name='devotee_delete'),
    path('sabhas/delete/<str:pk>/', views.sabha_delete, name='sabha_delete'),
    
    # Profile
    path('profile/', views.user_profile, name='user_profile'),
    
    # Mandal URLs
    path('mandals/', mandal_views.mandal_list, name='mandal_list'),
    path('mandals/add/', mandal_views.mandal_add, name='mandal_add'),
    path('mandals/delete/<str:pk>/', mandal_views.mandal_delete, name='mandal_delete'),
]