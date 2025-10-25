from django.urls import path
from .views import (
    create_attendance_session, sign_attendance, 
    attendance_summary_view, update_attendance_location,
    instant_attendance_history, instant_attendance_detail
)

urlpatterns = [
    path('create-new-attendance-session/<int:course_id>/', create_attendance_session, name='create_new_attendance_session'),
    path('sign-attendance/<int:attendance_id>/', sign_attendance, name='sign_attendance'),
    path('attendance-summary/<int:course_id>/', attendance_summary_view, name='attendance_summary'),
    path('instant-attendance-summary/<int:course_id>/', instant_attendance_history, name='instant_attendance_history'),
    path('instant-attendance-detail/<int:session_id>/', instant_attendance_detail, name='instant_attendance_detail'),
    path('update-attendance-location/<int:session_id>/', update_attendance_location, name='update_attendance_location'),
]