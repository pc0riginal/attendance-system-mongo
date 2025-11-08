from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Devotee URLs
    path('devotees/', views.devotee_list, name='devotee_list'),
    path('devotees/add/', views.devotee_add, name='devotee_add'),
    path('devotees/<int:pk>/', views.devotee_detail, name='devotee_detail'),
    path('devotees/edit/<int:pk>/', views.devotee_edit, name='devotee_edit'),
    
    # Sabha URLs
    path('sabhas/', views.sabha_list, name='sabha_list'),
    path('sabhas/add/', views.sabha_add, name='sabha_add'),
    path('sabhas/<int:sabha_id>/attendance/', views.mark_attendance, name='mark_attendance'),
    
    # Reports
    path('reports/', views.attendance_report, name='attendance_report'),
    path('reports/export/', views.export_attendance, name='export_attendance'),
    path('my-attendance/', views.devotee_attendance_history, name='devotee_history'),
    
    # Upload
    path('upload-devotees/', views.upload_devotees, name='upload_devotees'),
]