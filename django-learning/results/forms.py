from django import forms
from .models import Result

class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ['student', 'course', 'mid_term_marks', 'assignments_marks', 'final_exam_marks']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'mid_term_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '30'}),
            'assignments_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '20'}),
            'final_exam_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '50'}),
        }
