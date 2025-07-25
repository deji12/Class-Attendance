from .views import (
    available_courses, registered_courses,
    register_course, unregister_course,
    home_page, faq
)
from django.urls import path

urlpatterns = [
    path('', home_page, name='home_page'),
    path('available-courses/', available_courses, name='available_courses'),
    path('registered-courses/', registered_courses, name='registered_courses'),
    path('register-course/', register_course, name='register_course'),
    path('unregister-course/', unregister_course, name='unregister_course'),
    path('faq/', faq, name='faq'),
]