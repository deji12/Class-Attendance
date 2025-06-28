from django.contrib import admin
from .models import AttendanceRecord, AttendanceSession
from import_export.admin import ImportExportModelAdmin

class AttendanceRecordAdmin(ImportExportModelAdmin, admin.ModelAdmin):

    list_display = ['session', 'student', 'signed_in_at', 'ip_address', 'device']
    search_fields = ['session__course__code', 'student__username', 'ip_address']
    list_filter = ['session__course', 'signed_in_at']

admin.site.register(AttendanceRecord, AttendanceRecordAdmin)

class AttendanceSessionAdmin(ImportExportModelAdmin, admin.ModelAdmin):

    list_display = ['course__name', 'initiated_by', 'timestamp', 'duration']
    search_fields = ['course__code', 'initiated_by__username']
    list_filter = ['course', 'initiated_by', 'timestamp']

admin.site.register(AttendanceSession, AttendanceSessionAdmin)