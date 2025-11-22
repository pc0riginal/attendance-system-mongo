from django import forms
from .models import Devotee, Sabha, Attendance

class DevoteeMongoForm(forms.Form):
    SABHA_CHOICES = [
        ('bal', 'Bal Sabha'),
        ('yuvak', 'Yuvak Sabha'),
        ('mahila', 'Mahila Sabha'),
        ('sanyukt', 'Sanyukt Sabha'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    
    DEVOTEE_TYPE_CHOICES = [
        ('haribhakt', 'Haribhakt'),
        ('gunbhavi', 'Gunbhavi'),
        ('karyakar', 'Karyakar'),
    ]
    
    devotee_id = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auto-generated if empty'}))
    devotee_type = forms.ChoiceField(choices=DEVOTEE_TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    contact_number = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control'}))
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    age = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': True}))
    sabha_type = forms.ChoiceField(choices=SABHA_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    address_line = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    landmark = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    zone = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    join_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'capture': 'camera'
        })
    )
    
    def __init__(self, *args, **kwargs):
        allowed_sabha_types = kwargs.pop('allowed_sabha_types', [])
        super().__init__(*args, **kwargs)
        if allowed_sabha_types:
            self.fields['sabha_type'].choices = [
                (choice[0], choice[1]) for choice in self.SABHA_CHOICES 
                if choice[0] in allowed_sabha_types
            ]



class SabhaForm(forms.Form):
    SABHA_CHOICES = [
        ('bal', 'Bal Sabha'),
        ('yuvak', 'Yuvak Sabha'),
        ('mahila', 'Mahila Sabha'),
        ('sanyukt', 'Sanyukt Sabha'),
    ]
    
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    sabha_type = forms.ChoiceField(choices=SABHA_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    location = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}))
    
    def __init__(self, *args, **kwargs):
        allowed_sabha_types = kwargs.pop('allowed_sabha_types', [])
        super().__init__(*args, **kwargs)
        if allowed_sabha_types:
            self.fields['sabha_type'].choices = [
                (choice[0], choice[1]) for choice in self.SABHA_CHOICES 
                if choice[0] in allowed_sabha_types
            ]



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