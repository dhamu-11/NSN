from django.contrib import admin
from .models import Address, PersonalInformation, Academics,PersonalDocuments, Examination,HSC,HSCMarks,SSLC,SSLCMarks,BriefDetails,Hosteller,BankDetails,Scholarship,RejoinStudent,DiplomaMark,DiplomaStudent,SemesterMarksheet,DiplomaMarksheet
# Register your models here.
@admin.register(Academics)
class AcademicsAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'course', 'current_year', 'current_semester')
    search_fields = ( 'current_year', 'current_semester')
    list_filter = ('roll_number',)
    ordering = ('-current_semester',)

@admin.register(PersonalInformation)
class PersonalInformationAdmin(admin.ModelAdmin):
    list_display = ('roll_number',)
    search_fields = ( 'roll_number',)
    list_filter = ('roll_number',)
    
    
admin.site.register(PersonalDocuments)
admin.site.register(Examination)
admin.site.register(HSC)
admin.site.register(HSCMarks)
admin.site.register(SSLC)
admin.site.register(SSLCMarks)
admin.site.register(BriefDetails)
admin.site.register(Hosteller)
admin.site.register(BankDetails)
admin.site.register(Scholarship)
admin.site.register(RejoinStudent)
admin.site.register(DiplomaStudent)
admin.site.register(DiplomaMark)
admin.site.register(SemesterMarksheet)
admin.site.register(DiplomaMarksheet)