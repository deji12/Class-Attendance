from django.shortcuts import render, redirect
from .models import User, PasswordResetCode
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from .utils import is_valid_email, authenticate_user
from django.contrib.auth import login, logout
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from Core.models import Faculty, Department

def register_new_user(request):

    if request.method == 'POST':

        # get form data
        email = request.POST.get('email')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        matric_number = request.POST.get('matric_number')
        level = request.POST.get('level')
        department = request.POST.get('department')
        faculty = request.POST.get('faculty')

        if not (email and password and full_name and matric_number and level and department and faculty):
            messages.error(request, 'All fields must be filled')
            return redirect('register_new_user')
        
        if not is_valid_email(email):
            messages.error(request, 'Invalid email provided')
            return redirect('register_new_user')
        
        register_url_with_post_data_as_query_params = f"{reverse('register_new_user')}?email={email}&full_name={full_name}&matric_number={matric_number}&level={level}&department={department}&faculty={faculty}"   

        # check if user already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already in use')
            return redirect(register_url_with_post_data_as_query_params)
        
        if  User.objects.filter(matric_number=matric_number).exists():
            messages.error(request, 'Matric number already in use')
            return redirect(register_url_with_post_data_as_query_params)
        
        if len(password) < 5:
            messages.error(request, 'Password must not be at least 5 characters')
            return redirect(register_url_with_post_data_as_query_params)

        
        if not Faculty.objects.filter(name=faculty).exists():
            messages.error(request, 'Invalid faculty provided')
            return redirect(register_url_with_post_data_as_query_params)
        
        if not Department.objects.filter(name=department).exists():
            messages.error(request, 'Invalid department provided')
            return redirect(register_url_with_post_data_as_query_params)
        
        # create user
        User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
            matric_number=matric_number,
            level=level,
            department=Department.objects.get(name=department),
            faculty=Faculty.objects.get(name=faculty)
        )

        messages.success(request, 'Account created successfully, login')
        return redirect('login_user')

    context = {
        'levels': settings.STUDENT_LEVELS,
        'faculties': Faculty.objects.all(),
        'departments': Department.objects.all(),
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

        #login with email
        if '@' in matric_number_or_email:
            user = authenticate_user(
                value=matric_number_or_email,
                password=password,
                type='email'
            )

        # login with matric number
        elif '/' in matric_number_or_email:
            user = authenticate_user(
                value=matric_number_or_email,
                password=password,
                type='matric_number'
            )

        else:
            messages.error(request, 'Invalid login credentials provided')
            return redirect('login_user')

        if user is not None:
            login(request, user)
            return redirect('home_page')
        else:
            messages.error(request, 'Invalid login credentials provided')
            return redirect('login_user')

    return render(request, 'authentication/login.html')

def logout_user(request):
    logout(request)
    return redirect('login_user')

def forgot_password(request):

    if request.method == 'POST':
        email = request.POST.get('email')

        if not email or not is_valid_email(email):
            messages.error(request, 'Invalid email provided')
            return redirect('register_new_user')

        if not User.objects.filter(email=email).exists():
            messages.error(request, 'No user with that email exists')
            return redirect('forgot_password')
        
        user = User.objects.get(email=email)
        new_password_reset = PasswordResetCode(user=user)
        new_password_reset.save()
        
        user.send_password_reset_email(request, new_password_reset.reset_id)

        return redirect(f"{reverse('forgot_password')}?password_reset_sent=True?email={email}")

    return render(request, 'authentication/forgot_password.html')

def reset_password(request, reset_id):
    try:
        password_reset_id = PasswordResetCode.objects.get(reset_id=reset_id)

        if request.method == "POST":

            # grab form data
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            passwords_have_error = False

            # validate form data
            if password != confirm_password:
                passwords_have_error = True
                messages.error(request, 'Passwords do not match')

            if len(password) < 5:
                passwords_have_error = True
                messages.error(request, 'Password must be at least 5 characters long')

            expiration_time = password_reset_id.created_when + timezone.timedelta(minutes=10)

            # check if link has expired
            if timezone.now() > expiration_time:
                passwords_have_error = True
                messages.error(request, 'The reset link has expired.')

                password_reset_id.delete()

            # reset user password if no issues were found
            if not passwords_have_error:
                user = password_reset_id.user
                user.set_password(password)
                user.save()

                password_reset_id.delete()

                messages.success(request, 'Password reset successfully. Please proceed to login')
                return redirect('login_user')
            else:
                return redirect('reset_user_password', reset_id=reset_id)

    except PasswordResetCode.DoesNotExist:
        messages.error(request, 'Invalid reset ID')
        return redirect('forgot_password')

    return render(request, 'authentication/reset_password.html')

@login_required
def user_profile_setting(request):

    if request.method == 'POST':

        # get form data
        email = request.POST.get('email')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        matric_number = request.POST.get('matric_number')

        level = request.POST.get('level')
        # department = request.POST.get('department')
        # faculty = request.POST.get('faculty')

        user_data_updated = False
        user = request.user
        
        # validate data
        if not is_valid_email(email):
            messages.error(request, 'Invalid email provided')
            return redirect('user_profile_settings')  

        if email and User.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, 'Email already in use')
            return redirect('user_profile_settings')
        
        if  matric_number and User.objects.filter(matric_number=matric_number).exclude(id=user.id).exists():
            messages.error(request, 'Matric number already in use')
            return redirect('user_profile_settings')
        
        if password and len(password) < 5:
            messages.error(request, 'Password must not be at least 5 characters')
            return redirect('user_profile_settings')

        if password:
            if not user.check_password(password):
                user.set_password(password)

        if email and email != user.email:
            user.email = email
            
        if full_name and full_name != user.full_name:
            user.full_name = full_name

        if matric_number and matric_number != user.matric_number:
            user.matric_number = matric_number

        if level and user.level != level:
            user.level = level
            user_data_updated = True

        # if department and department != user.department:
        #     user.department = Department.objects.get(name=department)
        #     user_data_updated = True

        # if faculty and faculty != user.faculty:
        #     user.faculty = Faculty.objects.get(name=faculty)
        #     user_data_updated = True

        # only save user object if an update has been made
        if user_data_updated:
            user.save()
            messages.success(request, 'Settings updated successfully')

        return redirect('user_profile_settings')

    context = {
        'levels': settings.STUDENT_LEVELS,
        'faculties': Faculty.objects.all(),
        'departments': Department.objects.all(),
    }
    return render(request, 'authentication/user_profile_setting.html', context)