from django.shortcuts import render, redirect
from .models import AttendanceSession, AttendanceRecord
from User.decorators import class_representative_required
from Course.models import Course
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from .utils import get_user_ip, is_user_in_nigeria, haversine_distance
from User.models import User
from django.db import models
from django.conf import settings
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

@class_representative_required
def create_attendance_session(request, course_id):

    if request.method == 'POST':

        duration = request.POST.get('duration')
        longitude = request.POST.get('longitude')
        latitude = request.POST.get('latitude')

        instant_attendance = request.POST.get('instant_attendance')
        instant_attendance_title = request.POST.get('instant_attendance_title')

        previous_url = request.META['HTTP_REFERER']

        if not (duration and duration.isalnum()):
            messages.error(request, 'You must select a valid duration for this attendance session')
            return redirect(previous_url)
        
        # make sure the user is on a mobile device
        # if request.user_agent.is_bot or request.user_agent.is_pc:
        #     messages.error(request, "Attendance must be created using a mobile device.")
        #     return redirect(previous_url)
        
        if not (longitude and latitude):
            messages.error(request, 'You must provide your current location to initiate an attendance session')
            return redirect(previous_url)
        
        course = Course.objects.get(id=course_id)

        # instant attendance can be created regardless of whether an attendance has been taken already
        if instant_attendance != 'True':
            # Check if attendance already exists for today
            now = timezone.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)

            already_exists = AttendanceSession.objects.filter(
                course=course,
                timestamp__range=(today_start, today_end)
            ).exists()

            if already_exists:
                messages.error(request, f'An attendance session has already been created for {course.code} today.')
                return redirect(previous_url)
        
        try:
            attendance = AttendanceSession(
                course=course,
                initiated_by=request.user,
                duration=int(duration),
                initiator_latitude=latitude,
                initiator_longitude=longitude
            )

            if instant_attendance == 'True':
                attendance.is_instant_attendance = True
                attendance.instant_attendance_title = instant_attendance_title if instant_attendance_title else ''

            attendance.save()

            user_ip = get_user_ip(request)

            # Create attendance record
            AttendanceRecord.objects.create(
                session=attendance,
                student=request.user,
                ip_address=user_ip
            )

            messages.success(request, f'Attendance session for {course.code} created successfully and is valid for {duration} minutes')
            return redirect('registered_courses')

        except Course.DoesNotExist:
            messages.error(request, 'Invalid course')
            return redirect(previous_url)

@login_required
def sign_attendance(request, attendance_id):

    # make sure the user is on a mobile device
    if request.user_agent.is_bot or request.user_agent.is_pc:
        messages.error(request, "Attendance can only be signed in using a mobile device.")
        return redirect('registered_courses')
    
    attendance = AttendanceSession.objects.get(id=attendance_id)
    
    # Check if already signed in
    if AttendanceRecord.objects.filter(session=attendance, student=request.user).exists():
        messages.error(request, "You have already signed in for this attendance session.")
        return redirect('registered_courses')
    
    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('registered_courses')

    # Validate and parse coordinates early
    try:
        lat = float(request.POST.get('latitude'))
        lon = float(request.POST.get('longitude'))
    except (TypeError, ValueError):
        messages.error(request, "Invalid or missing location data.")
        return redirect('registered_courses')
    
    MAX_DISTANCE_KM = settings.MAX_DISTANCE_KM

    # Check if location is set
    if attendance.initiator_latitude is None or attendance.initiator_longitude is None:
        messages.error(request, "Attendance initiator location is not set.")
        return redirect('registered_courses')

    # Distance check
    distance = haversine_distance(
        attendance.initiator_latitude, attendance.initiator_longitude,
        lat, lon
    )

    if distance > MAX_DISTANCE_KM:
        messages.error(request, "You are too far from the attendance point to sign in.")
        return redirect('registered_courses')

    # Ensure session is still active
    if not attendance.course.has_active_attendance_session():
        messages.error(request, "No active attendance session for this course.")
        return redirect('registered_courses')
    
    if settings.DEBUG:
        user_ip = settings.DEFAULT_IP_ADDRESS
    else:
        user_ip = get_user_ip(request)

    if AttendanceRecord.objects.filter(session=attendance, ip_address=user_ip).exists():
        messages.error(request, "This device has already signed in for this attendance session.")
        return redirect('registered_courses')

    # Nigeria geo-check
    if not is_user_in_nigeria(user_ip):
        messages.error(request, "Attendance can only be signed in Nigeria.")
        return redirect('registered_courses')

    # Create attendance
    AttendanceRecord.objects.create(
        session=attendance,
        student=request.user,
        ip_address=user_ip
    )

    messages.success(request, "Attendance signed in successfully.")
    return redirect('registered_courses')
        
@class_representative_required
def attendance_summary_view(request, course_id):
    user = request.user
    course = Course.objects.get(id=course_id)
    
    # Get sessions only for this course
    sessions = AttendanceSession.objects.filter(course=course, is_instant_attendance=False).order_by('timestamp')
    
    # Get students in the same faculty/department/level
    students = User.objects.filter(
        faculty=user.faculty, 
        department=user.department, 
        level=user.level
    ).prefetch_related(
        models.Prefetch(
            'attendance_records',
            queryset=AttendanceRecord.objects.filter(session__course=course, session__is_instant_attendance=False),
            to_attr='course_attendance_records'
        )
    )

    attendance_data = []
    for student in students:
        # Only count records for this course's sessions
        records = {r.session_id for r in student.course_attendance_records}
        percentage = round((len(records)/sessions.count() * 100), 2) if sessions.exists() else 0
        
        attendance_data.append({
            'student': student,
            'sessions_present': records,
            'percentage': percentage
        })

    context = {
        'course': course,
        'sessions': sessions,
        'attendance_data': attendance_data,
    }
    return render(request, 'attendance/attendance_summary.html', context)

@class_representative_required
def update_attendance_location(request, session_id):

    # make sure the user is on a mobile device
    if request.user_agent.is_bot or request.user_agent.is_pc:
        messages.error(request, "Location update must be performed from a mobile device.")
        return redirect('registered_courses')
    
    if request.method != 'POST':
        return redirect('attendance_summary', course_id=session_id)
    
    body = json.loads(request.body)

    try:
        session = AttendanceSession.objects.get(id=session_id)
    except AttendanceSession.DoesNotExist:
        messages.error(request, "Invalid attendance session.")
        return redirect('attendance_summary', course_id=session_id)

    # Validate and parse coordinates
    try:
        lat = float(body.get('latitude'))
        lon = float(body.get('longitude'))
    except (TypeError, ValueError):
        messages.error(request, "Invalid or missing location data.")
        return redirect('attendance_summary', course_id=session.course.id)

    # Update the session's initiator location
    session.initiator_latitude = lat
    session.initiator_longitude = lon
    session.save()

    # messages.success(request, "Attendance location updated successfully.")
    # return redirect('attendance_summary', course_id=session.course.id)

    return JsonResponse(status=200, data={})

@class_representative_required
def instant_attendance_history(request, course_id):

    user = request.user
    course = Course.objects.get(id=course_id)
    
    # Get sessions only for this course
    sessions = AttendanceSession.objects.filter(course=course, is_instant_attendance=True).order_by('-timestamp')

    context = {
        'sessions': sessions
    }
    return render(request, 'attendance/instant_attendance_summary.html', context)

@class_representative_required
def instant_attendance_detail(request, session_id):

    try:
        session = AttendanceSession.objects.get(id=session_id)
    except AttendanceSession.DoesNotExist:
        messages.error(request, "Invalid attendance session.")
        return redirect('attendance_summary', course_id=session_id)
    
    attendance_records = AttendanceRecord.objects.filter(session=session)
    context = {
        'records': attendance_records,
        'session': session,
        'course': session.course
    }

    return render(request, 'attendance/instant_attendsnce_list_detail.html', context)