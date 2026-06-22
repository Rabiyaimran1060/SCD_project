from django import forms
from .models import Course

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'name', 'description']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course Code (e.g. CS-101)'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description...'}),
        }
