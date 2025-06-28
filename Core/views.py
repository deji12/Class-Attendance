from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from Course.models import Course
from django.contrib import messages
from django.http import JsonResponse
from User.models import User

@login_required
def home_page(request):

    return render(request, 'Core/home.html')

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


@login_required
def register_course(request):

    user = request.user

    if request.method == 'POST' and user.is_class_representative:
        course_id = request.POST.get('course_id')

        course = Course.objects.get(id=course_id)

        # Check if the course is already registered
        if course in user.courses_taking.all():
            return JsonResponse({
                'status': 'error', 
                'message': 'You are already registered for this course.'
            })
        
        user.courses_taking.add(course)
        user.save()
        
        return JsonResponse({
            'status': 'success', 
            'message': f'You have successfully registered for {course.name}.'
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

@login_required
def registered_courses(request):

    user = request.user

    # if current user is a class representative, get courses for that user
    
    if user.is_class_representative:
        courses = user.courses_taking.all()

    # else, get courses from the class representative of the user's faculty and department
    else:
        class_representative = User.objects.get(
            is_class_representative=True,
            faculty=user.faculty,
            department=user.department,
            level=user.level
        )
        courses = class_representative.courses_taking.all()

    context = {
        'courses': courses,
    }
    return render(request, 'Core/registered_courses.html', context)  

@login_required
def unregister_course(request):

    user = request.user

    if request.method == 'POST' and user.is_class_representative:
        course_id = request.POST.get('course_id')

        course = Course.objects.get(id=course_id)

        # Check if the course is registered
        if course not in user.courses_taking.all():
            return JsonResponse({
                'status': 'error', 
                'message': 'You are not registered for this course.'
            })
        
        user.courses_taking.remove(course)
        user.save()
        return JsonResponse({
            'status': 'success', 
            'message': f'You have successfully unregistered from {course.name}.'
        })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})