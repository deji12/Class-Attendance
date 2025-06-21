from django.urls import path
from .views import (
    register_new_user, login_user
)

urlpatterns = [
    path('register/', register_new_user, name='register_new_user'),
    path('login/', login_user, name='login_user'),
]