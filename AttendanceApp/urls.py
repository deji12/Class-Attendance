from django.urls import path
from .views import create_attendance_session, sign_attendance, attendance_summary_view

urlpatterns = [
    path('create-new-attendance-session/<int:course_id>/', create_attendance_session, name='create_new_attendance_session'),
    path('sign-attendance/<int:attendance_id>/', sign_attendance, name='sign_attendance'),
    path('attendance-summary/<int:course_id>/', attendance_summary_view, name='attendance_summary'),
]