from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Student
from .forms import StudentForm
from predictor.ml_engine import predict_student_performance

@login_required
def student_list(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    
    students = Student.objects.all()
    
    if query:
        students = students.filter(name__icontains=query) | students.filter(roll_no__icontains=query)
    if status_filter:
        students = students.filter(predicted_status=status_filter)
        
    context = {
        'students': students,
        'q': query,
        'status_filter': status_filter
    }
    return render(request, 'students/student_list.html', context)

@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    results = student.results.all()
    
    if request.method == 'POST' and 'predict' in request.POST:
        res = predict_student_performance(student)
        messages.success(request, f"Prediction updated for {student.name}: {res['status']} with {res['confidence']:.1f}% confidence.")
        return redirect('student_detail', pk=pk)

    context = {
        'student': student,
        'results': results
    }
    return render(request, 'students/student_detail.html', context)

@login_required
def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"Student {student.name} added successfully.")
            return redirect('student_list')
    else:
        form = StudentForm()
    return render(request, 'students/student_form.html', {'form': form, 'title': 'Add Student'})

@login_required
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"Student {student.name} updated successfully.")
            return redirect('student_detail', pk=pk)
    else:
        form = StudentForm(instance=student)
    return render(request, 'students/student_form.html', {'form': form, 'title': f'Edit Student: {student.name}'})

@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, "Student deleted successfully.")
        return redirect('student_list')
    return render(request, 'students/student_confirm_delete.html', {'student': student})
