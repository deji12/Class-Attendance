from .views import (
    register_courses, registered_courses
)
from django.urls import path

urlpatterns = [
    path('register-courses/', register_courses, name='register_courses'),
    path('registered-courses/', registered_courses, name='registered_courses'),
]