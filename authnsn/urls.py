from django.urls import path
from .views import StudentLogin, StaffLogin, Register, Profile, logout_user, home,get_nasa_apod
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .import views
urlpatterns = [
    path('', home, name='home'),
    path('get_nasa_apod/', views.get_nasa_apod, name='get_nasa_apod'),
    path('student/login/', StudentLogin.as_view(), name='student-login'),
    path('staff/login/', StaffLogin.as_view(), name='staff-login'),
    path('register/', Register.as_view(), name='register'),
    path('profile/', Profile.as_view(), name='profile'),
    path('logout/', logout_user, name='logout'),
    # JWT Token obtain route (for login and token generation)
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # JWT Token refresh route (for refreshing access token)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
