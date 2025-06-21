from django.shortcuts import render, redirect
from .models import User
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from .utils import is_valid_email, authenticate_user
from django.contrib.auth import login, logout

def register_new_user(request):

    if request.method == 'POST':

        # get form data
        email = request.POST.get('email')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        matric_number = request.POST.get('matric_number')
        level = request.POST.get('level')

        if not (email and password and full_name and matric_number and level):
            messages.error(request, 'All fields must be filled')
            return redirect('register_new_user')
        
        if not is_valid_email(email):
            messages.error(request, 'Invalid email provided')
            return redirect('register_new_user')
        
        register_url_with_post_data_as_query_params = f"{reverse('register_new_user')}?email={email}&full_name={full_name}&matric_number={matric_number}&level={level}"   

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already in use')
            return redirect(register_url_with_post_data_as_query_params)
        
        if  User.objects.filter(matric_number=matric_number).exists():
            messages.error(request, 'Matric number already in use')
            return redirect(register_url_with_post_data_as_query_params)
        
        if len(password) < 5:
            messages.error(request, 'Password must not be at least 5 characters')
            return redirect(register_url_with_post_data_as_query_params)
        
        # create user in database
        User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
            matric_number=matric_number,
            level=level
        )

        messages.success(request, 'Account created successfully, login')
        return redirect('login_user')

    context = {
        'levels': settings.STUDENT_LEVELS
    }
    return render(request, 'authentication/register.html', context)

def login_user(request):

    if request.method == 'POST':
        
        # get form data
        matric_number_or_email = request.POST.get('matric_number_or_email')
        password = request.POST.get('password')

        if not (matric_number_or_email and password):
            messages.error(request, 'All fields are required')
            return redirect('login_user')
        
        # authenticate login creds
        if '@' in matric_number_or_email:
            user = authenticate_user(
                value=matric_number_or_email,
                password=password,
                type='email'
            )
        elif '/' in matric_number_or_email:
            user = authenticate_user(
                value=matric_number_or_email,
                password=password,
                type='matric_number'
            )

        if user is not None:
            login(request, user)
            # return redirect('home')
        else:
            messages.error(request, 'Invalid login credentials provided')
            return redirect('login_user')

    return render(request, 'authentication/login.html')