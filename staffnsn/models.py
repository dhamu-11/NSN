from django.db import models
from  studentnsn.models import Academics, PersonalInformation
from django.core.exceptions import ValidationError
class StudentsAttendance(models.Model):
    class CurrentSemester(models.TextChoices):
        SEM1 = '1', '1'
        SEM2 = '2', '2'
        SEM3 = '3', '3'
        SEM4 = '4', '4'
        SEM5 = '5', '5'
        SEM6 = '6', '6'
        SEM7 = '7', '7'
        SEM8 = '8', '8'
        SEM9 = '9', '9'
        SEM10 = '10', '10'
    roll_number = models.BigIntegerField()
    semester = models.CharField(max_length=2, choices=CurrentSemester.choices,default=CurrentSemester.SEM1 )
    staff_name = models.TextField()
    Course_Code = models.TextField()
    Course_Name = models.CharField(max_length=100)
    Date_Attended = models.DateField()
    From_Time = models.TimeField()
    To_Time = models.TimeField()
    No_of_Hours = models.SmallIntegerField()
    Is_Present = models.BooleanField(default=False)  

class AttendancePercentage(models.Model): 
    roll_number = models.BigIntegerField()
    Semester = models.IntegerField()
    Course_Code = models.TextField(null=True, blank=True)  # Null for full course calculation
    Attendance_Percentage = models.FloatField()

class StaffAddress(models.Model):
    AREA_TYPE_CHOICES = [
        ('Urban', 'Urban'),
        ('Rural', 'Rural'),
    ]
    area_type = models.CharField(max_length=10, choices=AREA_TYPE_CHOICES)
    door_number = models.TextField()
    apartment_name = models.CharField(max_length=35, null=True, blank=True)
    street_name = models.CharField(max_length=35)
    taluk = models.CharField(max_length=35)
    block = models.CharField(max_length=35)
    district = models.CharField(max_length=35)
    state = models.CharField(max_length=35)
    pincode = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.door_number}, {self.street_name}, {self.taluk}, {self.district}, {self.state} - {self.pincode}"

class StaffPersonalInformation(models.Model):
    STAFF_TYPE_CHOICES = [
        (0, 'Professor'),
        (1, 'Associate Professor'),
        (2, 'Assistant Professor'),
    ]
    
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    
    staff_id= models.BigIntegerField(primary_key=True)
    designation = models.PositiveSmallIntegerField(choices=STAFF_TYPE_CHOICES)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    dob = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=5)
    religion = models.CharField(max_length=50)
    community = models.CharField(max_length=50)
    caste = models.CharField(max_length=50)
    nationality = models.CharField(max_length=50)
    staff_mobile = models.BigIntegerField()
    email = models.EmailField(unique=True)
    aadhar_number = models.BigIntegerField(unique=True)
    father_name = models.CharField(max_length=100)
    father_occupation = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    mother_occupation = models.CharField(max_length=100)
    father_mobile = models.BigIntegerField()
    mother_mobile = models.BigIntegerField()
    annual_income = models.DecimalField(max_digits=10, decimal_places=2)
    height = models.FloatField()
    weight = models.FloatField()
    permanent_address = models.ForeignKey(StaffAddress, related_name="permanent_address", on_delete=models.CASCADE)
    communication_address = models.ForeignKey(StaffAddress, related_name="communication_address", on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.staff_id})"