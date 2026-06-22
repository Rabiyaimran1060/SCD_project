from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def root_redirect(request):
    return redirect('dashboard')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_redirect, name='root'),
    path('accounts/', include('accounts.urls')),
    path('students/', include('students.urls')),
    path('courses/', include('courses.urls')),
    path('results/', include('results.urls')),
    path('predictor/', include('predictor.urls')),
]
