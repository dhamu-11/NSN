# views.py
from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from ..models import Academics, PersonalInformation,Scholarship,RejoinStudent
from datetime import datetime
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from django.db import transaction
import jwt
from django.conf import settings
from ..models import PersonalInformation, Address
from authnsn.models import Student
from rest_framework_simplejwt.authentication import JWTAuthentication
import logging
from ..models import PersonalInformation, Address
from authnsn.models import Student
from authnsn.session_manager import SessionManager

@method_decorator(ensure_csrf_cookie, name='dispatch')
class AcademicsView(View):
    authentication_classes = []
    permission_classes = [AllowAny]
    session_manager = SessionManager()

    def get_context(self, user):
        academic_data = Academics.objects.filter(roll_number__roll_number=user.username).first()
        return {
            'academic_data': academic_data,
            'courses': Academics.Course.choices,
            'years': Academics.CurrentYear.choices,
            'semesters': Academics.CurrentSemester.choices,
            'roll_number': user.username
        }

    def get(self, request):
        session_id = request.COOKIES.get('session_id')
        if not session_id:
            return redirect('student-login')
        
        try:
            session = SessionManager().get_session(session_id)
            if not session:
                raise jwt.InvalidTokenError()
            
            user = get_user_model().objects.get(id=session.user_id)
            if session.user_type != 'student':
                return HttpResponse('Unauthorized', status=403)
            
            context = self.get_context(user)
            if request.headers.get('HX-Request'):
                return render(request, 'academics/academics_form.html', context)
            return render(request, 'academics/academics.html', context)
            
        except (jwt.InvalidTokenError, get_user_model().DoesNotExist):
            response = redirect('student-login')
            response.delete_cookie('session_id')
            return response

    def post(self, request):
        session_id = request.COOKIES.get('session_id')
        if not session_id:
            return HttpResponse('Unauthorized', status=401)

        try:
            session = SessionManager().get_session(session_id)
            user = get_user_model().objects.get(id=session.user_id)
            personal_info = PersonalInformation.objects.get(roll_number=user.username)

            academic_data = {
                'roll_number': personal_info,
                'course': request.POST.get('course'),
                'department': request.POST.get('department'),
                'current_year': request.POST.get('current_year'),
                'current_semester': request.POST.get('current_semester'),
                'year_joining': datetime.strptime(request.POST.get('year_joining'), '%Y-%m-%d'),
                'type_of_admission': request.POST.get('type_of_admission'),
                'admission_type': request.POST.get('admission_type'),
                'emis_number': request.POST.get('emis_number'),
                'umis_number': request.POST.get('umis_number'),
                'class_incharge': request.POST.get('class_incharge'),
                'class_room_number': request.POST.get('class_room_number'),
            }

            academics, created = Academics.objects.update_or_create(
                roll_number=personal_info,
                defaults=academic_data
            )

            context = self.get_context(user)
            context['message'] = 'Academic information saved successfully!'
            return render(request, 'academics/academics_form.html', context)

        except (ValidationError, ValueError) as e:
            return HttpResponse(str(e), status=400)
        except Exception as e:
            return HttpResponse('An error occurred', status=500)
        

@method_decorator(ensure_csrf_cookie, name='dispatch')
class ScholarView(View):
    authentication_classes = []
    permission_classes = [AllowAny]
    session_manager = SessionManager()

    def get_context(self, user):
        s_data = Scholarship.objects.filter(roll_number__roll_number=user.username).first()
        return {
            's_data': s_data,
            'roll_number': user.username
        }

    def get(self, request):
        session_id = request.COOKIES.get('session_id')
        if not session_id:
            return redirect('student-login')
        
        try:
            session = SessionManager().get_session(session_id)
            if not session:
                raise jwt.InvalidTokenError()
            
            user = get_user_model().objects.get(id=session.user_id)
            if session.user_type != 'student':
                return HttpResponse('Unauthorized', status=403)
            
            context = self.get_context(user)
            if request.headers.get('HX-Request'):
                return render(request, 'Scholarship/s_form.html', context)
            return render(request, 'Scholarship/s_details.html', context)
            
        except (jwt.InvalidTokenError, get_user_model().DoesNotExist):
            response = redirect('student-login')
            response.delete_cookie('session_id')
            return response

    def post(self, request):
        session_id = request.COOKIES.get('session_id')
        if not session_id:
            return HttpResponse('Unauthorized', status=401)

        try:
            session = SessionManager().get_session(session_id)
            user = get_user_model().objects.get(id=session.user_id)
            personal_info = PersonalInformation.objects.get(roll_number=user.username)

            s_data = {
                'roll_number': personal_info,
                'scholarship_type': request.POST.get('scholarship_type'),
                'academic_year_availed': request.POST.get('academic_year_availed'),
                'availed': request.POST.get('availed') == 'true',
            }
              
            academics, created = Scholarship.objects.update_or_create(
                roll_number=personal_info,
                defaults= s_data
            )

            context = self.get_context(user)
            context['message'] = 'Scholarship information saved successfully!'
            return render(request, 'Scholarship/s_form.html', context)

        except (ValidationError, ValueError) as e:
            return HttpResponse(str(e), status=400)
        except Exception as e:
            return HttpResponse('An error occurred', status=500)
        

@method_decorator(ensure_csrf_cookie, name='dispatch')
class RejoinView(View):
    authentication_classes = []
    permission_classes = [AllowAny]
    session_manager = SessionManager()

    def get_context(self, user):
        r_data = RejoinStudent.objects.filter(roll_number__roll_number=user.username).first()
        return {
            'r_data': r_data,
            'roll_number': user.username
        }

    def get(self, request):
        session_id = request.COOKIES.get('session_id')
        if not session_id:
            return redirect('student-login')
        
        try:
            session = SessionManager().get_session(session_id)
            if not session:
                raise jwt.InvalidTokenError()
            
            user = get_user_model().objects.get(id=session.user_id)
            if session.user_type != 'student':
                return HttpResponse('Unauthorized', status=403)
            
            context = self.get_context(user)
            if request.headers.get('HX-Request'):
                return render(request, 'Student Details/rejoin/r_form.html', context)
            return render(request, 'Student Details/rejoin/r_details.html', context)
            
        except (jwt.InvalidTokenError, get_user_model().DoesNotExist):
            response = redirect('student-login')
            response.delete_cookie('session_id')
            return response

    def post(self, request):
        session_id = request.COOKIES.get('session_id')
        if not session_id:
            return HttpResponse('Unauthorized', status=401)

        try:
            session = SessionManager().get_session(session_id)
            user = get_user_model().objects.get(id=session.user_id)
            personal_info = PersonalInformation.objects.get(roll_number=user.username)

            r_data = {
                'roll_number': personal_info,
                'new_roll_number': request.POST.get('new_roll_number'),
                'previous_type_of_student': request.POST.get('previous_type_of_student'),
                'year_of_discontinue': request.POST.get('year_of_discontinue'),
                'year_of_rejoin': request.POST.get('year_of_rejoin'),
                'reason_for_discontinue': request.POST.get('reason_for_discontinue'),
            }

            rejoinstudent, created = RejoinStudent.objects.update_or_create(
                roll_number=personal_info,
                defaults=r_data
            )

            context = self.get_context(user)
            context['message'] = 'Rejoin information saved successfully!'
            return render(request, 'Student Details/rejoin/r_form.html', context)

        except (ValidationError, ValueError) as e:
            return HttpResponse(str(e), status=400)
        except Exception as e:
            return HttpResponse('An error occurred', status=500)
        


        

