import bcrypt
from rest_framework.views import APIView, View
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import SimpleRateThrottle
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from .models import Student, Staff, StaffPassword, StudentPassword
from .serializers import LoginSerializer, RegisterSerializer
from datetime import timedelta
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from django.conf import settings
import jwt
from .session_manager import SessionManager
from django.views.decorators.csrf import ensure_csrf_cookie


from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
import requests
from datetime import datetime, timezone

@ensure_csrf_cookie
def home(request):
    context = {
        'nasa_image': None,
        'nasa_title': None,
        'nasa_explanation': None,
        'image_date': None,
        'error_message': None
    }
    return render(request, 'base.html', context)

def get_nasa_apod(request):
    """HTMX endpoint for NASA APOD"""
    nasa_api_key = 'QQNax5jgRnaRiqzYHEgIIfIWYa5aMtgKKdYEvC7P'
    
    # Don't specify a date to get the latest available image
    nasa_url = f'https://api.nasa.gov/planetary/apod?api_key={nasa_api_key}'
    
    try:
        response = requests.get(nasa_url)
        response.raise_for_status()
        nasa_data = response.json()
        
        context = {
            'nasa_image': nasa_data.get('url'),
            'nasa_title': nasa_data.get('title'),
            'nasa_explanation': nasa_data.get('explanation'),
            'image_date': nasa_data.get('date')
        }
    except requests.RequestException as e:
        context = {
            'error_message': f"Failed to fetch NASA image: {str(e)}"
        }
    except Exception as e:
        context = {
            'error_message': f"An unexpected error occurred: {str(e)}"
        }
    
    return render(request, 'nasa_partial.html', context)
# Constants for cache keys

FAILED_ATTEMPTS_KEY_TEMPLATE = "failed_attempts_{identifier}_{role}"

# Utility function to generate JWT tokens
def generate_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh.set_exp(lifetime=timedelta(days=7))  # Set refresh token expiration to 7 days

    access_token = refresh.access_token
    access_token.set_exp(lifetime=timedelta(minutes=15))  # Set access token expiration to 15 minutes

    return {
        'refresh': str(refresh),
        'access': str(access_token),
    }

# Function to hash password using bcrypt
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

# Function to check if password matches the hashed password
def check_password(hashed_password, password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# Custom Throttling Logic for Login Attempts
def handle_throttling(identifier, role):
    cache_key = FAILED_ATTEMPTS_KEY_TEMPLATE.format(identifier=identifier, role=role)
    failed_attempts = cache.get(cache_key, 0)

    if failed_attempts >= 3:
        return True  # Too many failed attempts, throttle login

    return False


# Registration View for Students and Staff
class Register(APIView):
    permission_classes = [AllowAny]
    template_name = 'register.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        if request.headers.get('HX-Request'):
            serializer = RegisterSerializer(data=request.POST)
            if not serializer.is_valid():
                return HttpResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            data = serializer.validated_data
            password = data['password']

            if len(password) < 8:
                return Response({'error': 'Password must be at least 8 characters long'}, 
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                if 'roll_number' in data:
                    response = self.register_student(data)
                elif 'staff_id' in data:
                    response = self.register_staff(data)

                if response.status_code != 201:
                    return Response({'error': response.data.get('error', 'Registration failed')}, 
                                    status=response.status_code)
                    
                return Response({'message': 'Registration successful'}, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return render(request, self.template_name)
    
    def register_student(self, data):
        try:
            roll_number = data['roll_number']
            previous_roll_number = data.get('previous_roll_number')
            student_type = data['student_type']

            if previous_roll_number:
                # Validate previous roll number for rejoin students
                student = Student.objects.filter(
                    previous_roll_number=previous_roll_number,
                    student_type='rejoin'
                ).first()
                if not student:
                    return Response({'error': 'Previous roll number not found or not eligible for rejoining.'},
                                    status=status.HTTP_404_NOT_FOUND)
            else:
                # Validate roll number and student type
                student = Student.objects.get(roll_number=roll_number, student_type=student_type)

            if student.is_registered:
                return Response({'error': 'Student already registered'}, status=status.HTTP_400_BAD_REQUEST)

            # Hash password and save
            hashed_password = hash_password(data['password'])
            user = get_user_model().objects.create_user(username=roll_number, password=data['password'])
            StudentPassword.objects.create(identifier=roll_number, role='student', password_hash=hashed_password)

            student.is_registered = True
            student.save()

            return Response({'message': 'Student registered successfully'}, status=status.HTTP_201_CREATED)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found or mismatch in student type.'}, status=status.HTTP_404_NOT_FOUND)

    def register_staff(self, data):
        try:
            staff = Staff.objects.get(staff_id=data['staff_id'])
            if staff.is_registered:
                return Response({'error': 'Staff already registered'}, status=status.HTTP_400_BAD_REQUEST)

            # Hash the password
            hashed_password = hash_password(data['password'])

            user = get_user_model().objects.create_user(username=staff.staff_id, password=data['password'])
            StaffPassword.objects.create(identifier=staff.staff_id, role='staff', password_hash=hashed_password)

            staff.is_registered = True
            staff.save()
            return Response({'message': 'Staff registered successfully'}, status=status.HTTP_201_CREATED)
        except Staff.DoesNotExist:
            return Response({'error': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)


class StudentLogin(APIView):
    permission_classes = [AllowAny]
    session_manager = SessionManager()

    def get(self, request):
        session_id = request.COOKIES.get('session_id')
        if session_id:
            session = self.session_manager.get_session(session_id)
            if session and session.user_type == 'student':
                return redirect('profile')
        return render(request, 'login.html')

    def post(self, request):
        roll_number = request.data.get('roll_number')
        student_type = request.data.get('student_type')
        password = request.data.get('password')

        if handle_throttling(roll_number, student_type):
            return HttpResponse(
                """<div id="error-message" class="error-message">
                    Too many failed login attempts. Please try again after 24 hours.
                </div>""",
                status=429
            )

        try:
            student = Student.objects.get(roll_number=roll_number, student_type=student_type)
            user_password = StudentPassword.objects.get(identifier=roll_number, role='student')

            if check_password(user_password.password_hash, password):
                user = get_user_model().objects.get(username=roll_number)
                tokens = generate_tokens_for_user(user)
                
                session_id = self.session_manager.create_session(
                    user.id, 'student', tokens
                )

                cache.delete(FAILED_ATTEMPTS_KEY_TEMPLATE.format(
                    identifier=roll_number, role=student_type))

                response = HttpResponse()
                response['HX-Redirect'] = '/student/dash/'
                response.set_cookie(
                    'session_id',
                    session_id,
                    max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
                    **self.session_manager.cookie_settings
                )
                return response
            else:
                # Handle failed login attempts
                cache_key = FAILED_ATTEMPTS_KEY_TEMPLATE.format(
                    identifier=roll_number, role=student_type)
                failed_attempts = cache.get(cache_key, 0)
                cache.set(cache_key, failed_attempts + 1, timeout=86400)
                return HttpResponse(
                    """<div id="error-message" class="error-message">
                        Invalid credentials
                    </div>""",
                    status=401
                )
        except (Student.DoesNotExist, StudentPassword.DoesNotExist):
            return HttpResponse(
                """<div id="error-message" class="error-message">
                    Invalid credentials
                </div>""",
                status=401
            )

class StaffLogin(APIView):
    permission_classes = [AllowAny]
    session_manager = SessionManager()

    def get(self, request):
        session_id = request.COOKIES.get('session_id')
        if session_id:
            session = self.session_manager.get_session(session_id)
            if session and session.user_type == 'staff':
                return redirect('profile')
        return render(request, 'staff_login.html')

    def post(self, request):
        staff_id = request.data.get('staff_id')
        password = request.data.get('password')

        if handle_throttling(staff_id, 'staff'):
            return HttpResponse(
                """<div id="error-message" class="error-message">
                    Too many failed login attempts. Please try again after 24 hours.
                </div>""",
                status=429
            )

        try:
            staff = Staff.objects.get(staff_id=staff_id)
            user_password = StaffPassword.objects.get(identifier=staff_id, role='staff')

            if check_password(user_password.password_hash, password):
                user = get_user_model().objects.get(username=staff_id)
                tokens = generate_tokens_for_user(user)
                
                session_id = self.session_manager.create_session(
                    user.id, 'staff', tokens
                )

                cache.delete(FAILED_ATTEMPTS_KEY_TEMPLATE.format(
                    identifier=staff_id, role='staff'))

                response = HttpResponse()
                response['HX-Redirect'] = '/staff/dash/'
                response.set_cookie(
                    'session_id',
                    session_id,
                    max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
                    **self.session_manager.cookie_settings
                )
                return response
            else:
                cache_key = FAILED_ATTEMPTS_KEY_TEMPLATE.format(
                    identifier=staff_id, role='staff')
                failed_attempts = cache.get(cache_key, 0)
                cache.set(cache_key, failed_attempts + 1, timeout=86400)
                return HttpResponse(
                    """<div id="error-message" class="error-message">
                        Invalid credentials
                    </div>""",
                    status=401
                )
        except (Staff.DoesNotExist, StaffPassword.DoesNotExist):
            return HttpResponse(
                """<div id="error-message" class="error-message">
                    Invalid credentials
                </div>""",
                status=401
            )

class Profile(APIView):
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
            
            if session.user_type == 'staff':
                staff_data = Staff.objects.filter(staff_id=user.username).first()
                if staff_data:
                    context = {
                        'user_type': 'staff',
                        'staff_id': staff_data.staff_id,
                        'email': staff_data.email,
                        'name': staff_data.name if hasattr(staff_data, 'name') else None
                    }
                    return render(request, 'staff_profile.html', context)
            else:
                student_data = Student.objects.filter(roll_number=user.username).first()
                if student_data:
                    context = {
                        'user_type': 'student',
                        'roll_number': student_data.roll_number,
                        'student_type': student_data.student_type,
                        'email': student_data.email,
                        'name': student_data.name if hasattr(student_data, 'name') else None
                    }
                    return render(request, 'profile.html', context)

            return HttpResponse('Profile not found', status=404)
            
        except (jwt.InvalidTokenError, get_user_model().DoesNotExist):
            response = redirect('student-login')
            response.delete_cookie('session_id')
            return response

@api_view(['POST'])
@permission_classes([AllowAny])
def logout_user(request):
    session_manager = SessionManager()
    session_id = request.COOKIES.get('session_id')
    
    if session_id:
        session = session_manager.get_session(session_id)
        if session:
            session_manager.invalidate_session(session_id)
    
    response = redirect('home')
    response.delete_cookie('session_id')
    return response

# Token Refresh View
from rest_framework_simplejwt.views import TokenRefreshView

class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [IsAuthenticated]  # Restrict refresh to authenticated users



