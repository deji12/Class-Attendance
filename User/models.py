from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from Core.models import Faculty, Department
import uuid
from django.core.mail import EmailMessage
from django.conf import settings
from django.urls import reverse

STUDENT_LEVELS = (
    ('100', '100'),
    ('200', '200'),
    ('300', '300'),
    ('400', '400'),
    ('500', '500'),
)

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(unique=True, help_text="The student's unique email address.")
    full_name = models.CharField(max_length=30, default='', null=True, blank=True, help_text="The student's full name.")
    matric_number = models.CharField(max_length=20, unique=True, null=True, blank=True, help_text="The student's unique matriculation number.")
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True, blank=True, help_text="The faculty to which the student belongs.")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True, help_text="The department to which the student belongs.")    
    level = models.CharField(max_length=3, choices=STUDENT_LEVELS, default='100', help_text="The student's level of study.")

    # courses_taking = models.ManyToManyField(Course, blank=True, help_text="Courses the student is currently enrolled in.")

    is_class_representative = models.BooleanField(default=False, help_text="Indicates whether the user is a class representative. Defaults to False.")
    is_staff =  models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False, help_text="Indicates whether the user has all admin permissions. Defaults to False.")
    is_active = models.BooleanField(default=True, help_text="Indicates whether the user account is active. Defaults to False and user needs to verify email on signup before it can be set to True.")
    
    last_used_ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="The last IP address used by the user.")
    date_joined = models.DateTimeField(auto_now_add=True, help_text="The date and time when the user joined.")
    
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email
    
    def send_password_reset_email(self, request, reset_id):
        password_reset_url = reverse('reset_user_password', kwargs={'reset_id': reset_id})
        full_password_reset_url = f'{request.scheme}://{request.get_host()}{password_reset_url}'
        
        email_body = f'Reset your password using the link below:\n\n\n{full_password_reset_url}'
        
        email_message = EmailMessage(
            'Reset your password',
            email_body,
            settings.EMAIL_HOST_USER,
            [self.email]
        )
        
        email_message.fail_silently = True
        email_message.send()

    
class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, unique=True,editable=False)
    created_when = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Password reset for {self.user.username} at {self.created_when}'