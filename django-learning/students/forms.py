from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'roll_no', 'email', 'attendance_pct', 'study_hours_per_week']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'roll_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Roll Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'attendance_pct': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '100'}),
            'study_hours_per_week': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '168'}),
        }
