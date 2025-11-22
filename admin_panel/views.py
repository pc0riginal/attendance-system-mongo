from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout
from .mongodb_models import AdminUserManager
import json

def is_superuser(user):
    if user.is_superuser:
        return True
    try:
        admin_manager = AdminUserManager()
        admin_user = admin_manager.get_user_by_username(user.username)
        return admin_user and admin_user.is_admin
    except:
        return False

@login_required
@user_passes_test(is_superuser)
def admin_dashboard(request):
    admin_manager = AdminUserManager()
    users = admin_manager.get_all_users()
    
    context = {
        'users': users,
        'total_users': len(users),
        'admin_users': len([u for u in users if u.is_admin]),
        'regular_users': len([u for u in users if not u.is_admin])
    }
    return render(request, 'admin_panel/dashboard.html', context)

@login_required
@user_passes_test(is_superuser)
def create_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        allowed_sabha_types = request.POST.getlist('allowed_sabha_types')
        is_admin = request.POST.get('is_admin') == 'on'
        
        try:
            admin_manager = AdminUserManager()
            
            # Create admin user record in MongoDB only
            admin_manager.create_user(username, email, password, allowed_sabha_types, is_admin)
            
            messages.success(request, f'User {username} created successfully!')
            return redirect('admin_dashboard')
            
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error creating user: {str(e)}')
    
    sabha_choices = [
        ('bal', 'Bal Sabha'),
        ('yuvak', 'Yuvak Sabha'),
        ('mahila', 'Mahila Sabha'),
        ('sanyukt', 'Sanyukt Sabha')
    ]
    
    return render(request, 'admin_panel/create_user.html', {'sabha_choices': sabha_choices})

@login_required
@user_passes_test(is_superuser)
def edit_user(request, user_id):
    admin_manager = AdminUserManager()
    admin_user = admin_manager.get_user_by_id(user_id)
    
    if not admin_user:
        messages.error(request, 'User not found')
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        allowed_sabha_types = request.POST.getlist('allowed_sabha_types')
        is_admin = request.POST.get('is_admin') == 'on'
        password = request.POST.get('password')
        
        try:
            # Update admin user record in MongoDB only
            update_data = {
                'email': email,
                'allowed_sabha_types': allowed_sabha_types,
                'is_admin': is_admin
            }
            if password:
                update_data['password'] = password
            
            admin_manager.update_user(user_id, **update_data)
            
            messages.success(request, f'User {admin_user.username} updated successfully!')
            return redirect('admin_dashboard')
            
        except Exception as e:
            messages.error(request, f'Error updating user: {str(e)}')
    
    sabha_choices = [
        ('bal', 'Bal Sabha'),
        ('yuvak', 'Yuvak Sabha'),
        ('mahila', 'Mahila Sabha'),
        ('sanyukt', 'Sanyukt Sabha')
    ]
    
    return render(request, 'admin_panel/edit_user.html', {
        'admin_user': admin_user,
        'sabha_choices': sabha_choices
    })

@login_required
@user_passes_test(is_superuser)
def delete_user(request, user_id):
    if request.method == 'POST':
        admin_manager = AdminUserManager()
        admin_user = admin_manager.get_user_by_id(user_id)
        
        if admin_user:
            try:
                # Delete admin user record from MongoDB only
                admin_manager.delete_user(user_id)
                
                messages.success(request, f'User {admin_user.username} deleted successfully!')
            except Exception as e:
                messages.error(request, f'Error deleting user: {str(e)}')
        else:
            messages.error(request, 'User not found')
    
    return redirect('admin_dashboard')