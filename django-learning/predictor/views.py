import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from students.models import Student
from courses.models import Course
from results.models import Result
from .ml_engine import predict_student_performance, train_model, MODEL_PATH

@login_required
def dashboard_view(request):
    # KPIs
    total_students = Student.objects.count()
    total_courses = Course.objects.count()
    total_results = Result.objects.count()
    
    pass_count = Student.objects.filter(predicted_status='Pass').count()
    risk_count = Student.objects.filter(predicted_status='At-Risk').count()
    fail_count = Student.objects.filter(predicted_status='Fail').count()
    unpredicted_count = Student.objects.filter(predicted_status='Not Predicted').count()

    # Model status
    model_exists = os.path.exists(MODEL_PATH)
    model_modified = ""
    if model_exists:
        mtime = os.path.getmtime(MODEL_PATH)
        model_modified = timezone.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')

    # Chart 1: Grade Distribution
    all_results = Result.objects.all()
    grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
    for res in all_results:
        grade_counts[res.grade] = grade_counts.get(res.grade, 0) + 1

    # Chart 2: Attendance vs GPA Scatter Plot
    # We collect all students with results, calculate overall average GPA
    scatter_data = []
    for s in Student.objects.all():
        student_results = s.results.all()
        if student_results.exists():
            avg_gpa = sum(r.gpa for r in student_results) / len(student_results)
            # Add mapping for CSS status classes
            status_class = 'text-success' if s.predicted_status == 'Pass' else ('text-warning' if s.predicted_status == 'At-Risk' else 'text-danger')
            scatter_data.append({
                'name': s.name,
                'x': s.attendance_pct,
                'y': round(avg_gpa, 2),
                'status': s.predicted_status,
                'status_class': status_class
            })

    # Recent Predictions
    recent_predictions = Student.objects.exclude(predicted_status='Not Predicted').order_by('-prediction_date')[:5]

    # At-Risk and Failing students list for a helpful dashboard widget
    at_risk_students = Student.objects.filter(predicted_status__in=['At-Risk', 'Fail']).order_by('attendance_pct')

    context = {
        'total_students': total_students,
        'total_courses': total_courses,
        'total_results': total_results,
        'pass_count': pass_count,
        'risk_count': risk_count,
        'fail_count': fail_count,
        'unpredicted_count': unpredicted_count,
        'model_exists': model_exists,
        'model_modified': model_modified,
        'grade_labels': list(grade_counts.keys()),
        'grade_values': list(grade_counts.values()),
        'scatter_data': scatter_data,
        'recent_predictions': recent_predictions,
        'at_risk_students': at_risk_students,
    }
    return render(request, 'dashboard.html', context)

@login_required
def predict_all_view(request):
    students = Student.objects.all()
    if not students.exists():
        messages.error(request, "No students available to predict. Please add students first.")
        return redirect('dashboard')

    predicted_count = 0
    for s in students:
        predict_student_performance(s)
        predicted_count += 1

    messages.success(request, f"Successfully predicted performance for {predicted_count} students.")
    return redirect('dashboard')

@login_required
def retrain_model_view(request):
    try:
        train_model()
        messages.success(request, "Machine Learning model retrained successfully on updated data parameters.")
    except Exception as e:
        messages.error(request, f"Error retraining ML model: {str(e)}")
    return redirect('dashboard')
