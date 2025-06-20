from django.contrib import admin
from .models import User
from import_export.admin import ImportExportModelAdmin

class UserAdmin(ImportExportModelAdmin, admin.ModelAdmin):

    list_display = ['matric_number', 'full_name', 'faculty', 'department', 'level', 'is_class_representative']
    search_fields = ['email', 'full_name', 'matric_number']
    list_filter = ['faculty', 'department', 'level', 'is_class_representative', 'is_staff', 'is_superuser', 'is_active']
    ordering = ['-date_joined']
    list_per_page = 30

admin.site.register(User, UserAdmin)