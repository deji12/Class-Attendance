from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings

def register_courses(request):

    context = {
        'levels': settings.STUDENT_LEVELS
    }

    return render(request, 'Core/register_courses.html', context)

def registered_courses(request):

    return render(request, 'Core/registered_courses.html')