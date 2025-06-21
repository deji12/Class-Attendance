import re
from .models import User

def is_valid_email(email):

    # Regular expression for a valid email
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email))

def authenticate_user(value, password, type):

    # authenticate user with matric number or email

    try:
        if type == 'matric_number':
            user = User.objects.get(matric_number=value)
        elif type == 'email':
            user = User.objects.get(email=value)

        if user.check_password(password):
            return user
        return None
    except User.DoesNotExist:
        return None