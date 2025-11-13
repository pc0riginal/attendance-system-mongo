from django import forms
from .models import Devotee, Sabha, Attendance

class DevoteeForm(forms.ModelForm):
    photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'capture': 'camera'
        })
    )
    
    class Meta:
        model = Devotee
        fields = ['name', 'contact_number', 'date_of_birth', 'gender', 'age', 'sabha_type', 'address_line', 'landmark', 'zone', 'join_date']
        widgets = {
            'join_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}),
            'sabha_type': forms.Select(attrs={'class': 'form-control'}),
            'address_line': forms.TextInput(attrs={'class': 'form-control'}),
            'landmark': forms.TextInput(attrs={'class': 'form-control'}),
            'zone': forms.TextInput(attrs={'class': 'form-control'}),
        }

class SabhaForm(forms.ModelForm):
    class Meta:
        model = Sabha
        fields = ['date', 'sabha_type', 'location', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'sabha_type': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class DevoteeUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Excel File',
        help_text='Upload .xlsx or .xls file with devotee data',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls'
        })
    )
    sabha_type_filter = forms.ChoiceField(
        choices=[('', 'All Sabha Types')] + Devotee.SABHA_CHOICES,
        required=False,
        label='Sabha Type Filter',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean_excel_file(self):
        file = self.cleaned_data['excel_file']
        if file:
            if not file.name.endswith(('.xlsx', '.xls')):
                raise forms.ValidationError('Please upload a valid Excel file (.xlsx or .xls)')
            if file.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError('File size must be less than 5MB')
        return file