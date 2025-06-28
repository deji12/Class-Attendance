from django.db import models
from Course.models import Course
from User.models import User

class AttendanceSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendance_sessions')
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='initiated_attendance_sessions')
    timestamp = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(default=10, help_text="Session duration in minutes")

    initiator_latitude = models.FloatField(null=True, blank=True)
    initiator_longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.course.code} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class AttendanceRecord(models.Model):
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    signed_in_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device = models.CharField(max_length=100, null=True, blank=True)  # Optional, if you want

    class Meta:
        unique_together = ('session', 'student')  # Prevent duplicate records
