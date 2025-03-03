from django.urls import path
from .views1 import StaffPersonalInformationView  
from .views import StaffDashboard, AttendanceView, SaveAttendanceView,StudentListView
urlpatterns = [
    path('staff/dash/', StaffDashboard.as_view(), name='staff-dashboard'),
    path('staff/personal/', StaffPersonalInformationView.as_view(), name='staff-personal'),
   
    path('attendance/', AttendanceView.as_view(), name='attendance'),
    path('get-students/', StudentListView.as_view(), name='get_students'),
    path('save-attendance/', SaveAttendanceView.as_view(), name='save_attendance'),
    
    
   
]

