from django.contrib import admin
from .models import Devotee, Sabha, Attendance

@admin.register(Devotee)
class DevoteeAdmin(admin.ModelAdmin):
    list_display = ['name', 'sabha_type', 'contact_number', 'join_date']
    list_filter = ['sabha_type', 'join_date']
    search_fields = ['name', 'contact_number']

@admin.register(Sabha)
class SabhaAdmin(admin.ModelAdmin):
    list_display = ['sabha_type', 'date', 'location', 'start_time']
    list_filter = ['sabha_type', 'date']
    ordering = ['-date']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['devotee', 'sabha', 'status', 'marked_at']
    list_filter = ['status', 'sabha__sabha_type', 'sabha__date']
    search_fields = ['devotee__name']