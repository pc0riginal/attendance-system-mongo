from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Q
from django.core.paginator import Paginator

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import csv
import json
from .models import Devotee, Sabha, Attendance
from .forms import DevoteeMongoForm, SabhaForm, DevoteeUploadForm
from .utils import process_excel_file, save_devotees
import os
import tempfile

def get_user_sabha_types(user):
    """Get allowed sabha types for user from MongoDB"""
    if user.is_superuser:
        return [choice[0] for choice in Devotee.SABHA_CHOICES]
    
    try:
        from admin_panel.mongodb_models import AdminUserManager
        admin_manager = AdminUserManager()
        admin_user = admin_manager.get_user_by_username(user.username)
        if admin_user:
            # Return the allowed sabha types, empty list if none assigned
            return admin_user.allowed_sabha_types or []
        # If user not found in MongoDB, return empty list (no access)
        return []
    except Exception:
        # On error, return empty list (no access)
        return []

def can_user_delete(user):
    """Check if user has delete permission"""
    if user.is_superuser:
        return True
    
    try:
        from admin_panel.mongodb_models import AdminUserManager
        admin_manager = AdminUserManager()
        admin_user = admin_manager.get_user_by_username(user.username)
        if admin_user:
            return admin_user.can_delete
        return False
    except Exception:
        return False

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
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
    allowed_sabha_types = get_user_sabha_types(request.user)
    if not allowed_sabha_types:
        allowed_sabha_types = []
    
    total_devotees = Devotee.objects.filter(sabha_type__in=allowed_sabha_types).count() if allowed_sabha_types else 0
    recent_sabhas = Sabha.objects.filter(sabha_type__in=allowed_sabha_types)[:5] if allowed_sabha_types else []
    
    # Calculate attendance rate for user's sabha types only
    user_sabhas = Sabha.objects.filter(sabha_type__in=allowed_sabha_types) if allowed_sabha_types else []
    user_sabha_ids = [s.pk for s in user_sabhas]
    total_attendance_records = Attendance.objects.filter(sabha__pk__in=user_sabha_ids).count() if user_sabha_ids else 0
    present_records = Attendance.objects.filter(sabha__pk__in=user_sabha_ids, status='present').count() if user_sabha_ids else 0
    attendance_rate = round((present_records / total_attendance_records * 100) if total_attendance_records > 0 else 0)
    
    # This week's sabha count for user's types only
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    this_week_sabhas = Sabha.objects.filter(sabha_type__in=allowed_sabha_types, date__range=[week_start, week_end]).count() if allowed_sabha_types else 0
    
    # Attendance stats for last 4 weeks (user's sabha types only)
    attendance_stats = []
    for i in range(4):
        week_start = today - timedelta(weeks=i+1)
        week_end = today - timedelta(weeks=i)
        
        sabhas_count = Sabha.objects.filter(sabha_type__in=allowed_sabha_types, date__range=[week_start, week_end]).count() if allowed_sabha_types else 0
        present_count = Attendance.objects.filter(
            sabha__sabha_type__in=allowed_sabha_types,
            sabha__date__range=[week_start, week_end],
            status='present'
        ).count() if allowed_sabha_types else 0
        
        attendance_stats.append({
            'week': f"Week {i+1}",
            'sabhas': sabhas_count,
            'present': present_count
        })
    
    context = {
        'total_devotees': total_devotees,
        'recent_sabhas': recent_sabhas,
        'attendance_stats': attendance_stats,
        'attendance_rate': attendance_rate,
        'this_week_sabhas': this_week_sabhas,
    }
    return render(request, 'attendance/dashboard.html', context)

@login_required
def devotee_list(request):
    search_query = request.GET.get('search', '')
    allowed_sabha_types = get_user_sabha_types(request.user)
    
    if not allowed_sabha_types:
        messages.error(request, 'You do not have permission to view devotees.')
        return redirect('dashboard')
    
    devotees = Devotee.objects.filter(sabha_type__in=allowed_sabha_types).order_by('name')
    
    if search_query:
        devotees = devotees.filter(
            Q(name__icontains=search_query) | 
            Q(contact_number__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(devotees, 50)  # 50 devotees per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # AJAX response for search
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        devotees_data = [{
            'id': d.id,
            'name': d.name,
            'contact_number': d.contact_number,
            'sabha_type_display': d.get_sabha_type_display(),
            'age_group': d.age_group or 'N/A',
            'join_date': d.join_date.strftime('%Y-%m-%d'),
            'photo_url': d.photo_url or ''
        } for d in page_obj]
        
        return JsonResponse({
            'devotees': devotees_data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'page_number': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count
        })
    
    return render(request, 'attendance/devotee_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'total_count': paginator.count,
        'can_delete': can_user_delete(request.user)
    })

@login_required
def devotee_add(request):
    allowed_sabha_types = get_user_sabha_types(request.user)
    if not allowed_sabha_types:
        messages.error(request, 'You do not have permission to add devotees.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = DevoteeMongoForm(request.POST, allowed_sabha_types=allowed_sabha_types)
        if form.is_valid():
            devotee = form.save(commit=False)
            if devotee.sabha_type not in allowed_sabha_types:
                messages.error(request, 'You can only add devotees for your assigned sabha types.')
                return render(request, 'attendance/devotee_form.html', {'form': form, 'title': 'Add Devotee'})
            devotee.save()
            messages.success(request, 'Devotee added successfully!')
            return redirect('devotee_list')
    else:
        form = DevoteeMongoForm(allowed_sabha_types=allowed_sabha_types)
    return render(request, 'attendance/devotee_form.html', {'form': form, 'title': 'Add Devotee'})

@login_required
def devotee_detail(request, pk):
    devotee = get_object_or_404(Devotee, pk=pk)
    allowed_sabha_types = get_user_sabha_types(request.user)
    
    # Check if user can view this devotee's sabha type
    if devotee.sabha_type not in allowed_sabha_types:
        messages.error(request, 'You do not have permission to view this devotee.')
        return redirect('devotee_list')
    
    return render(request, 'attendance/devotee_detail.html', {'devotee': devotee})

@login_required
def devotee_edit(request, pk):
    devotee = get_object_or_404(Devotee, pk=pk)
    allowed_sabha_types = get_user_sabha_types(request.user)
    
    # Check if user can edit this devotee's sabha type
    if devotee.sabha_type not in allowed_sabha_types:
        messages.error(request, 'You do not have permission to edit this devotee.')
        return redirect('devotee_list')
    
    if request.method == 'POST':
        form = DevoteeMongoForm(request.POST, instance=devotee, allowed_sabha_types=allowed_sabha_types)
        if form.is_valid():
            updated_devotee = form.save(commit=False)
            if updated_devotee.sabha_type not in allowed_sabha_types:
                messages.error(request, 'You can only assign sabha types you have access to.')
                return render(request, 'attendance/devotee_form.html', {'form': form, 'title': 'Edit Devotee', 'devotee': devotee})
            updated_devotee.save()
            messages.success(request, 'Devotee updated successfully!')
            return redirect('devotee_detail', pk=devotee.pk)
    else:
        form = DevoteeMongoForm(instance=devotee, allowed_sabha_types=allowed_sabha_types)
    return render(request, 'attendance/devotee_form.html', {'form': form, 'title': 'Edit Devotee', 'devotee': devotee})

@login_required
def sabha_list(request):
    allowed_sabha_types = get_user_sabha_types(request.user)
    print(f"DEBUG: User {request.user.username} allowed types: {allowed_sabha_types}")
    if not allowed_sabha_types:
        messages.error(request, 'You do not have permission to view sabhas.')
        return redirect('dashboard')
    sabhas = Sabha.objects.filter(sabha_type__in=allowed_sabha_types)
    print(f"DEBUG: Found {len(sabhas)} sabhas after filtering")
    for sabha in sabhas:
        print(f"DEBUG: Sabha - Date: {sabha.date}, Type: {sabha.sabha_type}, Location: {sabha.location}")
    return render(request, 'attendance/sabha_list.html', {'sabhas': sabhas})

@login_required
def sabha_add(request):
    allowed_sabha_types = get_user_sabha_types(request.user)
    if not allowed_sabha_types:
        messages.error(request, 'You do not have permission to create sabhas.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SabhaForm(request.POST, allowed_sabha_types=allowed_sabha_types)
        if form.is_valid():
            sabha_type = form.cleaned_data['sabha_type']
            if sabha_type not in allowed_sabha_types:
                messages.error(request, 'You can only create sabhas for your assigned sabha types.')
                return render(request, 'attendance/sabha_form.html', {'form': form, 'title': 'Create Sabha'})
            
            # Create sabha manually since we're not using ModelForm
            sabha = Sabha(
                date=form.cleaned_data['date'],
                sabha_type=sabha_type,
                location=form.cleaned_data['location'],
                start_time=form.cleaned_data['start_time'],
                end_time=form.cleaned_data['end_time']
            )
            sabha.save()
            messages.success(request, 'Sabha created successfully!')
            return redirect('sabha_list')
    else:
        form = SabhaForm(allowed_sabha_types=allowed_sabha_types)
    return render(request, 'attendance/sabha_form.html', {'form': form, 'title': 'Create Sabha'})

@login_required
def mark_attendance(request, sabha_id):
    sabha = get_object_or_404(Sabha, pk=sabha_id)
    allowed_sabha_types = get_user_sabha_types(request.user)
    
    # Check if user can access this sabha type
    if sabha.sabha_type not in allowed_sabha_types:
        messages.error(request, 'You do not have permission to mark attendance for this sabha type.')
        return redirect('sabha_list')
    
    search_query = request.GET.get('search', '')
    devotees = Devotee.objects.filter(sabha_type=sabha.sabha_type).order_by('name')
    
    if search_query:
        devotees = devotees.filter(
            Q(name__icontains=search_query) | 
            Q(contact_number__icontains=search_query)
        )
    
    # Pagination for large lists
    paginator = Paginator(devotees, 100)  # 100 devotees per page for attendance
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    devotees = page_obj
    
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
    
    # AJAX response for search
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        devotees_data = []
        for d in devotees:
            attendance = existing_attendance.get(d.id)
            devotees_data.append({
                'id': d.id,
                'name': d.name,
                'contact_number': d.contact_number,
                'sabha_type_display': d.get_sabha_type_display(),
                'photo_url': d.photo_url or '',
                'attendance_status': attendance.status if attendance else 'absent',
                'attendance_notes': attendance.notes if attendance else ''
            })
        
        return JsonResponse({
            'devotees': devotees_data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'page_number': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count
        })
    
    context = {
        'sabha': sabha,
        'devotees': devotees,
        'page_obj': page_obj,
        'existing_attendance': existing_attendance,
        'search_query': search_query,
        'total_count': paginator.count
    }
    return render(request, 'attendance/mark_attendance.html', context)

def is_admin_user(user):
    if user.is_superuser:
        return True
    try:
        from admin_panel.mongodb_models import AdminUserManager
        admin_manager = AdminUserManager()
        admin_user = admin_manager.get_user_by_username(user.username)
        return admin_user and admin_user.is_admin
    except:
        return False

@login_required
@user_passes_test(is_admin_user)
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
@user_passes_test(is_admin_user)
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

@login_required
@require_POST
def save_individual_attendance(request):
    try:
        data = json.loads(request.body)
        sabha_id = data.get('sabha_id')
        devotee_id = data.get('devotee_id')
        status = data.get('status', 'absent')
        notes = data.get('notes', '')
        
        sabha = get_object_or_404(Sabha, pk=sabha_id)
        devotee = get_object_or_404(Devotee, pk=devotee_id)
        
        attendance, created = Attendance.objects.get_or_create(
            devotee=devotee,
            sabha=sabha,
            defaults={'status': status, 'notes': notes}
        )
        
        if not created:
            attendance.status = status
            attendance.notes = notes
            attendance.save()
        
        return JsonResponse({'success': True, 'message': 'Attendance saved'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def user_profile(request):
    allowed_sabha_types = get_user_sabha_types(request.user)
    
    # Get user details from MongoDB
    try:
        from admin_panel.mongodb_models import AdminUserManager
        admin_manager = AdminUserManager()
        admin_user = admin_manager.get_user_by_username(request.user.username)
    except:
        admin_user = None
    
    # Define sabha choices
    sabha_choices = [('bal', 'Bal Sabha'), ('yuvak', 'Yuvak Sabha'), ('mahila', 'Mahila Sabha'), ('sanyukt', 'Sanyukt Sabha')]
    
    context = {
        'user': request.user,
        'admin_user': admin_user,
        'allowed_sabha_types': allowed_sabha_types,
        'sabha_type_display': [choice[1] for choice in sabha_choices if choice[0] in allowed_sabha_types]
    }
    return render(request, 'attendance/user_profile.html', context)