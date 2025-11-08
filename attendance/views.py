from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Count, Q
from datetime import datetime, timedelta
import csv
from .models import Devotee, Sabha, Attendance
from .forms import DevoteeForm, SabhaForm, AttendanceForm, DevoteeUploadForm
from .utils import process_excel_file, save_devotees
import os
import tempfile

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid credentials')
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    total_devotees = Devotee.objects.count()
    recent_sabhas = Sabha.objects.all()[:5]
    
    # Attendance stats for last 4 weeks
    today = datetime.now().date()
    four_weeks_ago = today - timedelta(weeks=4)
    
    attendance_stats = []
    for i in range(4):
        week_start = today - timedelta(weeks=i+1)
        week_end = today - timedelta(weeks=i)
        
        sabhas_count = Sabha.objects.filter(date__range=[week_start, week_end]).count()
        present_count = Attendance.objects.filter(
            sabha__date__range=[week_start, week_end],
            status='present'
        ).count()
        
        attendance_stats.append({
            'week': f"Week {i+1}",
            'sabhas': sabhas_count,
            'present': present_count
        })
    
    context = {
        'total_devotees': total_devotees,
        'recent_sabhas': recent_sabhas,
        'attendance_stats': attendance_stats,
    }
    return render(request, 'attendance/dashboard.html', context)

@login_required
def devotee_list(request):
    devotees = Devotee.objects.all()
    return render(request, 'attendance/devotee_list.html', {'devotees': devotees})

@login_required
def devotee_add(request):
    if request.method == 'POST':
        form = DevoteeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Devotee added successfully!')
            return redirect('devotee_list')
    else:
        form = DevoteeForm()
    return render(request, 'attendance/devotee_form.html', {'form': form, 'title': 'Add Devotee'})

@login_required
def devotee_detail(request, pk):
    devotee = get_object_or_404(Devotee, pk=pk)
    return render(request, 'attendance/devotee_detail.html', {'devotee': devotee})

@login_required
def devotee_edit(request, pk):
    devotee = get_object_or_404(Devotee, pk=pk)
    if request.method == 'POST':
        form = DevoteeForm(request.POST, instance=devotee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Devotee updated successfully!')
            return redirect('devotee_detail', pk=devotee.pk)
    else:
        form = DevoteeForm(instance=devotee)
    return render(request, 'attendance/devotee_form.html', {'form': form, 'title': 'Edit Devotee'})

@login_required
def sabha_list(request):
    sabhas = Sabha.objects.all()
    return render(request, 'attendance/sabha_list.html', {'sabhas': sabhas})

@login_required
def sabha_add(request):
    if request.method == 'POST':
        form = SabhaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sabha created successfully!')
            return redirect('sabha_list')
    else:
        form = SabhaForm()
    return render(request, 'attendance/sabha_form.html', {'form': form, 'title': 'Create Sabha'})

@login_required
def mark_attendance(request, sabha_id):
    sabha = get_object_or_404(Sabha, pk=sabha_id)
    devotees = Devotee.objects.filter(sabha_type=sabha.sabha_type)
    
    if request.method == 'POST':
        for devotee in devotees:
            status = request.POST.get(f'status_{devotee.id}', 'absent')
            notes = request.POST.get(f'notes_{devotee.id}', '')
            
            attendance, created = Attendance.objects.get_or_create(
                devotee=devotee,
                sabha=sabha,
                defaults={'status': status, 'notes': notes}
            )
            if not created:
                attendance.status = status
                attendance.notes = notes
                attendance.save()
        
        messages.success(request, 'Attendance marked successfully!')
        return redirect('sabha_list')
    
    # Get existing attendance
    existing_attendance = {
        att.devotee.id: att for att in Attendance.objects.filter(sabha=sabha)
    }
    
    context = {
        'sabha': sabha,
        'devotees': devotees,
        'existing_attendance': existing_attendance,
    }
    return render(request, 'attendance/mark_attendance.html', context)

@login_required
def attendance_report(request):
    sabhas = Sabha.objects.all()
    devotees = Devotee.objects.all()
    
    # Filter options
    sabha_type = request.GET.get('sabha_type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    attendance_qs = Attendance.objects.all()
    
    if sabha_type:
        attendance_qs = attendance_qs.filter(sabha__sabha_type=sabha_type)
    if date_from:
        attendance_qs = attendance_qs.filter(sabha__date__gte=date_from)
    if date_to:
        attendance_qs = attendance_qs.filter(sabha__date__lte=date_to)
    
    attendance_records = attendance_qs.select_related('devotee', 'sabha')
    
    context = {
        'attendance_records': attendance_records,
        'sabha_types': Devotee.SABHA_CHOICES,
        'filters': {
            'sabha_type': sabha_type,
            'date_from': date_from,
            'date_to': date_to,
        }
    }
    return render(request, 'attendance/attendance_report.html', context)

@login_required
def export_attendance(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Devotee Name', 'Sabha Type', 'Date', 'Status', 'Notes'])
    
    sabha_type = request.GET.get('sabha_type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    attendance_qs = Attendance.objects.all()
    
    if sabha_type:
        attendance_qs = attendance_qs.filter(sabha__sabha_type=sabha_type)
    if date_from:
        attendance_qs = attendance_qs.filter(sabha__date__gte=date_from)
    if date_to:
        attendance_qs = attendance_qs.filter(sabha__date__lte=date_to)
    
    for attendance in attendance_qs.select_related('devotee', 'sabha'):
        writer.writerow([
            attendance.devotee.name,
            attendance.sabha.get_sabha_type_display(),
            attendance.sabha.date,
            attendance.get_status_display(),
            attendance.notes
        ])
    
    return response

@login_required
def devotee_attendance_history(request):
    if hasattr(request.user, 'devotee'):
        devotee = request.user.devotee
        attendance_records = Attendance.objects.filter(devotee=devotee).select_related('sabha')
        return render(request, 'attendance/devotee_history.html', {
            'devotee': devotee,
            'attendance_records': attendance_records
        })
    else:
        messages.error(request, 'You are not registered as a devotee.')
        return redirect('dashboard')

@login_required
def upload_devotees(request):
    if request.method == 'POST':
        form = DevoteeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = form.cleaned_data['excel_file']
            sabha_type_filter = form.cleaned_data.get('sabha_type_filter')
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                for chunk in excel_file.chunks():
                    tmp_file.write(chunk)
                tmp_file_path = tmp_file.name
            
            try:
                # Process the Excel file
                result, error = process_excel_file(tmp_file_path, sabha_type_filter)
                
                if error:
                    messages.error(request, error)
                    return render(request, 'attendance/upload_devotees.html', {'form': form})
                
                valid_rows = result['valid_rows']
                errors = result['errors']
                
                if errors:
                    # Show validation errors
                    context = {
                        'form': form,
                        'errors': errors,
                        'total_rows': len(valid_rows) + len(errors),
                        'valid_count': len(valid_rows),
                        'error_count': len(errors)
                    }
                    return render(request, 'attendance/upload_devotees.html', context)
                
                # Save valid data
                created_count, updated_count = save_devotees(valid_rows)
                
                messages.success(
                    request, 
                    f'✅ Successfully imported {created_count} new devotees and updated {updated_count} existing devotees!'
                )
                return redirect('devotee_list')
                
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
    else:
        form = DevoteeUploadForm()
    
    return render(request, 'attendance/upload_devotees.html', {'form': form})