from .views import (
    available_courses, registered_courses,
    register_course,
)
from django.urls import path

urlpatterns = [
    path('available-courses/', available_courses, name='available_courses'),
    path('registered-courses/', registered_courses, name='registered_courses'),
    path('register-course/', register_course, name='register_course'),
]