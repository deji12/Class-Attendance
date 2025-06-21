from django.urls import path
from .views import (
    register_new_user, login_user,
    logout_user, forgot_password,
    reset_password,
)

urlpatterns = [
    path('register/', register_new_user, name='register_new_user'),
    path('login/', login_user, name='login_user'),
    path('logout/', logout_user, name='logout_user'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/<str:reset_id>/',reset_password, name='reset_user_password')
]