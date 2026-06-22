from django.db import models
from students.models import Student
from courses.models import Course

class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='results')
    mid_term_marks = models.FloatField(default=0.0, help_text="Marks out of 30")
    assignments_marks = models.FloatField(default=0.0, help_text="Marks out of 20")
    final_exam_marks = models.FloatField(default=0.0, help_text="Marks out of 50")
    
    class Meta:
        unique_together = ('student', 'course')

    @property
    def total_marks(self):
        return self.mid_term_marks + self.assignments_marks + self.final_exam_marks

    @property
    def grade(self):
        total = self.total_marks
        if total >= 85:
            return 'A'
        elif total >= 70:
            return 'B'
        elif total >= 55:
            return 'C'
        elif total >= 40:
            return 'D'
        else:
            return 'F'

    @property
    def gpa(self):
        total = self.total_marks
        if total >= 85: return 4.0
        elif total >= 80: return 3.7
        elif total >= 75: return 3.3
        elif total >= 70: return 3.0
        elif total >= 65: return 2.7
        elif total >= 60: return 2.3
        elif total >= 55: return 2.0
        elif total >= 50: return 1.7
        elif total >= 45: return 1.3
        elif total >= 40: return 1.0
        else: return 0.0

    def __str__(self):
        return f"{self.student.name} - {self.course.code}: {self.grade} ({self.total_marks})"
