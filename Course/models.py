from django.db import models
from Core.models import Department, Faculty

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
