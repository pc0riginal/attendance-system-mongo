from django.db import models
from django.contrib.auth.models import User

class Devotee(models.Model):
    SABHA_CHOICES = [
        ('bal', 'Bal Sabha'),
        ('yuvak', 'Yuvak Sabha'),
        ('mahila', 'Mahila Sabha'),
        ('sanyukt', 'Sanyukt Sabha'),
    ]
    
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    age_group = models.CharField(max_length=20)
    sabha_type = models.CharField(max_length=20, choices=SABHA_CHOICES)
    address = models.TextField()
    join_date = models.DateField()
    photo_url = models.URLField(max_length=500, blank=True, null=True, help_text='Google Drive or image URL')
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_sabha_type_display()}"

class Sabha(models.Model):
    SABHA_CHOICES = [
        ('bal', 'Bal Sabha'),
        ('yuvak', 'Yuvak Sabha'),
        ('mahila', 'Mahila Sabha'),
        ('sanyukt', 'Sanyukt Sabha'),
    ]
    
    date = models.DateField()
    sabha_type = models.CharField(max_length=20, choices=SABHA_CHOICES)
    location = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.get_sabha_type_display()} - {self.date}"

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ]
    
    devotee = models.ForeignKey(Devotee, on_delete=models.CASCADE)
    sabha = models.ForeignKey(Sabha, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='absent')
    notes = models.TextField(blank=True)
    marked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['devotee', 'sabha']
    
    def __str__(self):
        return f"{self.devotee.name} - {self.sabha} - {self.get_status_display()}"