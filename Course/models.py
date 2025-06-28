from django.db import models
from Core.models import Department, Faculty
from django.utils import timezone
from datetime import timedelta

STUDENT_LEVELS = (
    ('100', '100'),
    ('200', '200'),
    ('300', '300'),
    ('400', '400'),
    ('500', '500'),
)

SEMESTER = (
    ('First', 'First'),
    ('Second', 'Second')
)

class Course(models.Model):
    name = models.CharField(max_length=100, help_text="The name of the course.")
    code = models.CharField(max_length=10, unique=True, help_text="The unique code for the course.")
    level = models.CharField(max_length=20, help_text="The level at which the course is offered.", choices=STUDENT_LEVELS, default='100')
    semester = models.CharField(max_length=10, choices=SEMESTER, default='First', help_text="The semester in which the course is offered.")
    description = models.TextField(blank=True, null=True, help_text="A brief description of the course.")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses', help_text="The department to which this course belongs.")
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='courses', help_text="The faculty to which this course belongs.")
    number_of_initiated_attendances = models.IntegerField(default=0, help_text="The number of initiated attendances for this course.")
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def has_active_attendance_session(self):

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        session = self.attendance_sessions.filter(
            timestamp__range=(today_start, today_end)
        ).first()

        if session:
            expiration_time = session.timestamp + timedelta(minutes=session.duration)
            return now <= expiration_time
        
        return False
    
    def get_last_attendance_session_id(self):

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        session = self.attendance_sessions.filter(
            timestamp__range=(today_start, today_end)
        ).first()

        return session.id