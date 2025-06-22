from django.contrib import admin
from .models import Course
from import_export.admin import ImportExportModelAdmin

class CourseAdmin(ImportExportModelAdmin, admin.ModelAdmin):

    list_display = ['name', 'code', 'faculty', 'department', 'level', 'semester']
    list_filter = ['level', 'semester', 'faculty', 'department']
    search_fields = ['name', 'code']

admin.site.register(Course, CourseAdmin)