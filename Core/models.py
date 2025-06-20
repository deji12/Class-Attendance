from django.db import models

class Faculty(models.Model):
    name = models.CharField(max_length=100, help_text="The name of the faculty.")
    description = models.TextField(blank=True, null=True, help_text="A brief description of the faculty.")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Faculties"
    
class Department(models.Model):
    name = models.CharField(max_length=100, help_text="The name of the department.")
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments', help_text="The faculty to which this department belongs.")
    description = models.TextField(blank=True, null=True, help_text="A brief description of the department.")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Departments"