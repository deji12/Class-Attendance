from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Faculty, Department

class FacultyAdmin(ImportExportModelAdmin, admin.ModelAdmin):

    list_display = ['name', 'description']
    search_fields = ['name', 'description']

admin.site.register(Faculty, FacultyAdmin)

class DepartmentAdmin(ImportExportModelAdmin, admin.ModelAdmin):

    list_display = ['name', 'faculty', 'description']
    search_fields = ['name', 'faculty__name', 'description']
    list_filter = ['faculty']

admin.site.register(Department, DepartmentAdmin)