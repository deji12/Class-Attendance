from django.urls import path
from .views import (
    create_attendance_session, sign_attendance, 
    attendance_summary_view, update_attendance_location
)

urlpatterns = [
    path('create-new-attendance-session/<int:course_id>/', create_attendance_session, name='create_new_attendance_session'),
    path('sign-attendance/<int:attendance_id>/', sign_attendance, name='sign_attendance'),
    path('attendance-summary/<int:course_id>/', attendance_summary_view, name='attendance_summary'),
    path('update-attendance-location/<int:session_id>/', update_attendance_location, name='update_attendance_location'),
]