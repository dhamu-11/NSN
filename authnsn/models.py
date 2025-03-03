from django.db import models
from django.core.validators import RegexValidator

from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import RegexValidator

class Student(models.Model):
    STUDENT_TYPE_CHOICES = [
        ('regular', 'Regular'),
        ('lateral', 'Lateral'),
        ('rejoin', 'Rejoin')
    ]

    roll_number = models.CharField(max_length=20, unique=True)
    previous_roll_number = models.CharField(max_length=20, blank=True, null=True)
    student_type = models.CharField(max_length=10, choices=STUDENT_TYPE_CHOICES)
    previous_student_type = models.CharField(max_length=10, choices=STUDENT_TYPE_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField()
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    rejoin_date = models.DateField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    is_registered = models.BooleanField(default=False)

    def clean(self):
        # Check if student type is 'rejoin', then validate the required fields
        if self.student_type == 'rejoin':
            if not self.previous_roll_number:
                raise ValidationError('Previous roll number is required for rejoin students.')
            if not self.previous_student_type:
                raise ValidationError('Previous student type is required for rejoin students.')
            if not self.rejoin_date:
                raise ValidationError('Rejoin date is required for rejoin students.')
            if not self.reason:
                raise ValidationError('Reason is required for rejoin students.')
        else:
            # Ensure the rejoin-related fields are empty for non-rejoin students
            if self.previous_roll_number or self.previous_student_type or self.rejoin_date or self.reason:
                raise ValidationError('Previous student details and rejoin date are not required for non-rejoin students.')

    def _str_(self):
        return f"{self.roll_number} - {self.get_student_type_display()}"
    
class Staff(models.Model):
    staff_id = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField()
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(
        max_length=15, 
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$', 
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    is_registered = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    def _str_(self):
        return f"{self.staff_id}"

class StudentPassword(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student')
    ]

    identifier = models.CharField(max_length=20)  # roll_number or staff_id
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    password_hash = models.CharField(max_length=255)
    salt = models.CharField(max_length=255)  # Optional if you use Django's password hashers
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('identifier', 'role')

    def __str__(self):
        return f"{self.role.capitalize()} - {self.identifier}"
    
class StaffPassword(models.Model):
    ROLE_CHOICES = [
        ('staff', 'Staff')
    ]

    identifier = models.CharField(max_length=20)  # roll_number or staff_id
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    password_hash = models.CharField(max_length=255)
    salt = models.CharField(max_length=255)  # Optional if you use Django's password hashers
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('identifier', 'role')

    def __str__(self):
        return f"{self.role.capitalize()} - {self.identifier}"
    

from django.db import models
from django.conf import settings
from datetime import datetime, timedelta

class UserSession(models.Model):
    session_id = models.CharField(max_length=64, unique=True)
    user_id = models.IntegerField()
    user_type = models.CharField(max_length=10)  # 'student' or 'staff'
    access_token = models.TextField()
    refresh_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_sessions'
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['user_id']),
            models.Index(fields=['user_type']),
        ]
