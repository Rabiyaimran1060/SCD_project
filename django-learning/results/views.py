from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Result
from .forms import ResultForm

@login_required
def result_list(request):
    query = request.GET.get('q', '')
    results = Result.objects.select_related('student', 'course').all()
    if query:
        results = results.filter(student__name__icontains=query) | results.filter(course__name__icontains=query) | results.filter(course__code__icontains=query)
    return render(request, 'results/result_list.html', {'results': results, 'q': query})

@login_required
def result_create(request):
    if request.method == 'POST':
        form = ResultForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data['student']
            course = form.cleaned_data['course']
            
            # Check if duplicate entry
            if Result.objects.filter(student=student, course=course).exists():
                form.add_error(None, f"A result for {student.name} in {course.code} already exists. Please edit the existing result instead.")
            else:
                result = form.save()
                messages.success(request, f"Result added for {student.name} in {course.code}.")
                return redirect('result_list')
    else:
        initial_data = {}
        student_id = request.GET.get('student')
        if student_id:
            initial_data['student'] = student_id
        form = ResultForm(initial=initial_data)
    return render(request, 'results/result_form.html', {'form': form, 'title': 'Add Marks/Results'})

@login_required
def result_update(request, pk):
    result = get_object_or_404(Result, pk=pk)
    if request.method == 'POST':
        form = ResultForm(request.POST, instance=result)
        if form.is_valid():
            result = form.save()
            messages.success(request, f"Result updated for {result.student.name} in {result.course.code}.")
            return redirect('result_list')
    else:
        form = ResultForm(instance=result)
    return render(request, 'results/result_form.html', {'form': form, 'title': f'Edit Marks: {result.student.name} - {result.course.code}'})

@login_required
def result_delete(request, pk):
    result = get_object_or_404(Result, pk=pk)
    if request.method == 'POST':
        result.delete()
        messages.success(request, "Result deleted successfully.")
        return redirect('result_list')
    return render(request, 'results/result_confirm_delete.html', {'result': result})
