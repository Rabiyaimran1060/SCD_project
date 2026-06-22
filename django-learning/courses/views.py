from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course
from .forms import CourseForm

@login_required
def course_list(request):
    query = request.GET.get('q', '')
    courses = Course.objects.all()
    if query:
        courses = courses.filter(name__icontains=query) | courses.filter(code__icontains=query)
    return render(request, 'courses/course_list.html', {'courses': courses, 'q': query})

@login_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f"Course {course.name} added successfully.")
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'courses/course_form.html', {'form': form, 'title': 'Create Course'})

@login_required
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            course = form.save()
            messages.success(request, f"Course {course.name} updated successfully.")
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/course_form.html', {'form': form, 'title': f'Edit Course: {course.code}'})

@login_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        messages.success(request, "Course deleted successfully.")
        return redirect('course_list')
    return render(request, 'courses/course_confirm_delete.html', {'course': course})
