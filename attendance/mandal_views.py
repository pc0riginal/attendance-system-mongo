from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime
from bson import ObjectId

from .mongodb_utils import MongoDBManager

# Initialize MongoDB manager for mandals
mandals_db = MongoDBManager('mandals')

@login_required
def mandal_list(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to manage mandals.')
        return redirect('dashboard')
    
    mandals = list(mandals_db.find(sort=[('name', 1)]))
    for mandal in mandals:
        mandal['id'] = str(mandal['_id'])
    
    context = {'mandals': mandals}
    return render(request, 'attendance/mandal_list.html', context)

@login_required
def mandal_add(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to add mandals.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip().lower()
        display_name = request.POST.get('display_name', '').strip()
        
        if not name or not display_name:
            messages.error(request, 'Name and display name are required.')
            return render(request, 'attendance/mandal_form.html', {'title': 'Add Mandal'})
        
        # Check if mandal already exists
        if mandals_db.find_one({'name': name}):
            messages.error(request, f'Mandal "{name}" already exists.')
            return render(request, 'attendance/mandal_form.html', {'title': 'Add Mandal'})
        
        mandal_data = {
            'name': name,
            'display_name': display_name,
            'created_at': datetime.now().isoformat(),
            'created_by': request.user.username
        }
        
        mandals_db.insert_one(mandal_data)
        messages.success(request, f'Mandal "{display_name}" added successfully!')
        return redirect('mandal_list')
    
    return render(request, 'attendance/mandal_form.html', {'title': 'Add Mandal'})

@login_required
def mandal_delete(request, pk):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete mandals.')
        return redirect('dashboard')
    
    mandal = mandals_db.find_one({'_id': ObjectId(pk)})
    if not mandal:
        messages.error(request, 'Mandal not found')
        return redirect('mandal_list')
    
    if request.method == 'POST':
        mandals_db.delete_one({'_id': ObjectId(pk)})
        messages.success(request, f'Mandal "{mandal["display_name"]}" deleted successfully!')
        return redirect('mandal_list')
    
    return JsonResponse({'name': mandal['display_name']})