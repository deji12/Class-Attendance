from django.shortcuts import render, redirect
from .models import AttendanceSession, AttendanceRecord
from User.decorators import class_representative_required
from Course.models import Course
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from .utils import get_user_ip, verify_user_location, haversine_distance
from User.models import User
from django.db import models

@class_representative_required
def create_attendance_session(request, course_id):

    if request.method == 'POST':

        duration = request.POST.get('duration')
        longitude = request.POST.get('longitude')
        latitude = request.POST.get('latitude')


        if not (duration and duration.isalnum()):
            messages.error(request, 'You must select a valid duration for this attendance session')
            return redirect('registered_courses')
        
        if not (longitude and latitude):
            messages.error(request, 'You must provide your current location to initiate an attendance session')
            return redirect('registered_courses')
        
        course = Course.objects.get(id=course_id)

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
            return redirect('registered_courses')
        
        try:
            attendance = AttendanceSession(
                course=course,
                initiated_by=request.user,
                duration=int(duration),
                initiator_latitude=latitude,
                initiator_longitude=longitude
            )
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
            return redirect('registered_courses')

@login_required      
def sign_attendance(request, attendance_id):

    if request.method == 'POST':
        
        try:
            attendance = AttendanceSession.objects.get(id=attendance_id)

            lat = float(request.POST.get('latitude'))
            lon = float(request.POST.get('longitude'))

            # Distance threshold in km (e.g., 0.1 km = 100 meters)
            MAX_DISTANCE_KM = 0.1

            if attendance.initiator_latitude and attendance.initiator_longitude:
                distance = haversine_distance(
                    attendance.initiator_latitude, attendance.initiator_longitude,
                    lat, lon
                )

                if distance > MAX_DISTANCE_KM:
                    messages.error(request, "You are too far from the attendance point to sign in.")
                    return redirect('registered_courses')
                
                # Check if the attendance session is active
                if not attendance.course.has_active_attendance_session():
                    messages.error(request, 'No active attendance session for this course')
                    return redirect('registered_courses')
            
            # Check if the attendance session is still valid
            if AttendanceRecord.objects.filter(session=attendance, student=request.user).exists():
                messages.error(request, 'You have already signed in for this attendance session')
                return redirect('registered_courses')
            
            # get the user's IP address
            user_ip = get_user_ip(request)
            
            # Check if a user has already signed in from this IP address
            if AttendanceRecord.objects.filter(session=attendance, ip_address=user_ip):
                messages.error(request, "This device has already signed in for this attendance session")
                return redirect('registered_courses')
            
            # verify user location
            if not verify_user_location(user_ip):
                messages.error(request, 'Attendance can only be signed in Nigeria')
                return redirect('registered_courses')
            
            # Create attendance record
            AttendanceRecord.objects.create(
                session=attendance,
                student=request.user,
                ip_address=user_ip
            )

            messages.success(request, 'Attendance signed in successfully')
            return redirect('registered_courses')

        except AttendanceSession.DoesNotExist:
            messages.error(request, 'Attendance session does not exist')
            return redirect('registered_courses')
        
# views.py
@class_representative_required
def attendance_summary_view(request, course_id):
    user = request.user
    course = Course.objects.get(id=course_id)
    
    # Get sessions only for this course
    sessions = AttendanceSession.objects.filter(course=course).order_by('timestamp')
    
    # Get students in the same faculty/department/level
    students = User.objects.filter(
        faculty=user.faculty, 
        department=user.department, 
        level=user.level
    ).prefetch_related(
        models.Prefetch(
            'attendance_records',
            queryset=AttendanceRecord.objects.filter(session__course=course),
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