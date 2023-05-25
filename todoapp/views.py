from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json

from .models import Task, UserProfile
from .forms import TaskForm

def update_task(request, task_id):
    task = Task.objects.get(pk=task_id)

    if request.method == 'POST':
        data = json.loads(request.body)
        completed = data.get('completed')
        task.completed = completed
        task.save()

        return JsonResponse({'success': True})

    return JsonResponse({'success': False})


@login_required(login_url='home')
def task_list(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        # Создать профиль пользователя, если его нет
        user_profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user_profile = user_profile
            task.save()
            return redirect('task_list')
    else:
        form = TaskForm()

    tasks = Task.objects.filter(user_profile=user_profile)
    return render(request, 'todoapp/task.html', {'tasks': tasks, 'form': form})


def home(request):
    return render(request, 'todoapp/home.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('task_list')  # Перенаправление на главную страницу после регистрации
    else:
        form = UserCreationForm()
    return render(request, 'todoapp/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('base')  # Перенаправление на главную страницу после авторизации
    else:
        form = AuthenticationForm()
    return render(request, 'todoapp/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('base')


@login_required(login_url='home')
def delete_task(request, task_id):
    task = Task.objects.get(pk=task_id)
    task.delete()
    return redirect('task_list')



