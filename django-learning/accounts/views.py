from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm
from django.contrib import messages

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account has been created.")
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})
