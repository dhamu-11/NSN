import bcrypt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from studentnsn.models import Academics, PersonalInformation
from authnsn.models import Staff
from .models import StudentsAttendance,AttendancePercentage
from authnsn.session_manager import SessionManager
import jwt

class StaffDashboard(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    session_manager = SessionManager()

    def get(self, request):
        session_id = request.COOKIES.get('session_id')
        if not session_id:
            return redirect('student-login')
        
        try:
            session = self.session_manager.get_session(session_id)
            if not session:
                raise jwt.InvalidTokenError()
            
            user = get_user_model().objects.get(id=session.user_id)
            staff_data = Staff.objects.filter(staff_id=user.username).first()
            if staff_data:
                context = {
                    'user_type': 'staff',
                    'staff_id': staff_data.staff_id,
                    'email': staff_data.email,
                    'name': getattr(staff_data, 'name', None)
                }
                return render(request, 'staff_dashboard.html', context)

            return HttpResponse('Profile not found', status=404)
            
        except (jwt.InvalidTokenError, get_user_model().DoesNotExist):
            response = redirect('student-login')
            response.delete_cookie('session_id')
            return response

# views.py
from django.views import View
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.contrib.auth import get_user_model
import jwt
import re

class AttendanceView(View):
    template_name = 'attendance/attendance_form.html'

    def get_session_user(self, request):
        session_id = request.COOKIES.get('session_id')
        if not session_id:
            return None

        try:
            session = SessionManager().get_session(session_id)
            if not session:
                raise jwt.InvalidTokenError()
            
            return get_user_model().objects.get(id=session.user_id)
        except (jwt.InvalidTokenError, get_user_model().DoesNotExist):
            return None

    def get(self, request):
        user = self.get_session_user(request)
        if not user:
            response = redirect('student-login')
            response.delete_cookie('session_id')
            return response

        csrf_token = get_token(request)
        context = {
            'csrf_token': csrf_token,
            'semesters': Academics.CurrentSemester.choices,
            'current_user': user
        }

        if request.headers.get('HX-Request'):
            return render(request, 'attendance/attendance_form_partial.html', context)
        return render(request, self.template_name, context)

class StudentListView(View):
    template_name = 'attendance/student_list.html'

    def get(self, request):
        semester = request.GET.get('semester')
        if not semester:
            return HttpResponse("Semester is required", status=400)

        students = Academics.objects.filter(
            current_semester=semester
        ).select_related('roll_number')

        context = {
            'students': students,
        }
        
        return render(request, self.template_name, context)


from datetime import datetime

class SaveAttendanceView(View):
    def post(self, request):
        try:
            # Debug print
            print("Received POST data:", request.POST)
            
            # Get form data with validation
            course_code = request.POST.get('course_code')
            course_name = request.POST.get('course_name')
            staff_name = request.POST.get('staff_name')
            date_attended = request.POST.get('date_attended')
            from_time = request.POST.get('from_time')
            to_time = request.POST.get('to_time')
            no_of_hours = request.POST.get('no_of_hours')
            semester = request.POST.get('semester')
            present_students = request.POST.getlist('present_students[]')

            # Validate required fields
            required_fields = {
                'course_code': course_code,
                'course_name': course_name,
                'staff_name': staff_name,
                'date_attended': date_attended,
                'from_time': from_time,
                'to_time': to_time,
                'no_of_hours': no_of_hours,
                'semester': semester
            }

            missing_fields = [field for field, value in required_fields.items() if not value]
            if missing_fields:
                return JsonResponse({
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }, status=400)

            # Parse date and validate
            try:
                date_attended = datetime.strptime(date_attended, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }, status=400)

            # Get all students for the semester
            students = Academics.objects.filter(
                current_semester=semester
            ).select_related('roll_number')

            if not students.exists():
                return JsonResponse({
                    'error': f'No students found for semester {semester}'
                }, status=400)

            # Create attendance records
            attendance_records = []
            for student in students:
                roll_number_str = str(student.roll_number)  # Ensure it's a string
                roll_number_match = re.search(r'\((\d+)\)', roll_number_str)
                roll_number = roll_number_match.group(1) if roll_number_match else None  
                attendance_records.append(
                    StudentsAttendance(
                        roll_number=roll_number,
                        semester=semester, 
                        staff_name=staff_name,
                        Course_Code=course_code,
                        Course_Name=course_name,
                        Date_Attended=date_attended,
                        From_Time=from_time,
                        To_Time=to_time,
                        No_of_Hours=int(no_of_hours),
                        Is_Present=str(student.roll_number.roll_number) in present_students
                    )
                )

            # Bulk create the records
            StudentsAttendance.objects.bulk_create(attendance_records)
            
            return JsonResponse({
                'message': 'Attendance saved successfully!',
                'count': len(attendance_records)
            })

        except Exception as e:
            print(f"Error saving attendance: {str(e)}")  # Debug print
            return JsonResponse({
                'error': f'Error saving attendance: {str(e)}'
            }, status=400)
            

