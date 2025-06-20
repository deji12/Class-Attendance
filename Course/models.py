from django.db import models
from User.models import User
from Core.models import Department, Faculty

class Course(models.Model):
    name = models.CharField(max_length=100, help_text="The name of the course.")
    code = models.CharField(max_length=10, unique=True, help_text="The unique code for the course.")
    description = models.TextField(blank=True, null=True, help_text="A brief description of the course.")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses', help_text="The department to which this course belongs.")
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='courses', help_text="The faculty to which this course belongs.")

    def __str__(self):
        return f"{self.name} ({self.code})"
