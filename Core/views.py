from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from Course.models import Course
from django.contrib import messages

@login_required
def available_courses(request):

    user = request.user
    context = {
        'levels': settings.STUDENT_LEVELS,
        'semesters': ['First', 'Second'],
    }

    if request.method == 'POST':

        level = request.POST.get('level')
        semester = request.POST.get('semester')

        if not (level or semester):
            messages.error(request, 'A level and (or) semester must be selected')
            return redirect('available_courses')

        get_courses_for_current_user = Course.objects.filter(
            faculty=user.faculty,
            department=user.department
        )

        # filter by level
        if level:
            get_courses_for_current_user = get_courses_for_current_user.filter(level=level)
            context['level_filter'] = level

        # filter by semester
        if semester:
            get_courses_for_current_user = get_courses_for_current_user.filter(semester=semester)
            context['semester_filter'] = semester
            
            # if level was not filled, set default level as user's current level
            if not level:
                get_courses_for_current_user = get_courses_for_current_user.filter(level=user.level)
                context['level_filter'] = user.level
            
    else:
        get_courses_for_current_user = Course.objects.filter(
            level=user.level,
            faculty=user.faculty,
            department=user.department
        )
        
    context['courses'] = get_courses_for_current_user

    return render(request, 'Core/available_courses.html', context)

def registered_courses(request):

    return render(request, 'Core/registered_courses.html')