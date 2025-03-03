from django.contrib import admin
from django.contrib import admin
from .models import StudentsAttendance,StaffAddress,AttendancePercentage,StaffPersonalInformation
# Register your models here.
admin.site.register(StudentsAttendance)
admin.site.register(StaffPersonalInformation)
admin.site.register(StaffAddress)
