from django.db import models

class Student(models.Model):
    STATUS_CHOICES = [
        ('Pass', 'Pass'),
        ('At-Risk', 'At-Risk'),
        ('Fail', 'Fail'),
        ('Not Predicted', 'Not Predicted'),
    ]

    name = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    attendance_pct = models.FloatField(default=80.0, help_text="Attendance percentage (0-100)")
    study_hours_per_week = models.IntegerField(default=10, help_text="Weekly study hours")
    
    # ML Prediction fields
    predicted_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Predicted')
    prediction_confidence = models.FloatField(default=0.0, help_text="Confidence percentage (0-100)")
    prediction_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.roll_no})"
