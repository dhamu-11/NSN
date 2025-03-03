from django.views import View
from django.utils.decorators import method_decorator
from ..models import BriefDetails, PersonalInformation,Hosteller,BankDetails,Academics,SSLC,HSC,Scholarship,DiplomaStudent,RejoinStudent
from django.views import View
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from authnsn.models import Student
from authnsn.session_manager import SessionManager
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import jwt

class ReportDetails(View):
    authentication_classes = []
    permission_classes = [AllowAny]
    session_manager = SessionManager()

    def get(self, request):
        """Handle GET request to show the PDF generation form"""
        session_id = request.COOKIES.get('session_id')
        
        if not session_id:
            return redirect('student-login')
        
        try:
            session = self.session_manager.get_session(session_id)
            if not session:
                raise jwt.InvalidTokenError()

            user = get_user_model().objects.get(id=session.user_id)
            
            # Check if user is a student
            student_data = Student.objects.filter(roll_number=user.username).first()
            if student_data:
                context = {
                    'user_type': 'student',
                    'roll_number': student_data.roll_number,
                    'student_type': student_data.student_type,
                    'email': student_data.email,
                    'name': student_data.name if hasattr(student_data, 'name') else None
                }
                return render(request, 'report.html', context)

            return HttpResponse('Profile not found', status=404)
            
        except (jwt.InvalidTokenError, get_user_model().DoesNotExist):
            response = redirect('student-login')
            response.delete_cookie('session_id')
            return response

    def generate_personal_info_table(self, user_data):
        """Generate table for personal information"""
        data = [
            ['Personal Information'],
            ['Roll Number', str(user_data.roll_number)],
            ['Previous Roll Number', str(user_data.previous_roll_number) if user_data.previous_roll_number else 'N/A'],
            ['Type of Student', dict(PersonalInformation.STUDENT_TYPE_CHOICES)[user_data.type_of_student]],
            ['First Name', user_data.first_name],
            ['Last Name', user_data.last_name],
            ['Date of Birth', str(user_data.dob)],
            ['Gender', user_data.gender],
            ['Blood Group', user_data.blood_group],
            ['Religion', user_data.religion],
            ['Community', user_data.community],
            ['Caste', user_data.caste],
            ['Nationality', user_data.nationality],
            ['Student Mobile', str(user_data.student_mobile)],
            ['Email', user_data.email],
            ['Aadhar Number', str(user_data.aadhar_number)],
            ['Father Name', user_data.father_name],
            ['Father Occupation', user_data.father_occupation],
            ['Father Mobile', str(user_data.father_mobile)],
            ['Mother Name', user_data.mother_name],
            ['Mother Occupation', user_data.mother_occupation],
            ['Mother Mobile', str(user_data.mother_mobile)],
            ['Annual Income', str(user_data.annual_income)],
            ['Height', str(user_data.height)],
            ['Weight', str(user_data.weight)],
            ['Differently Abled', 'Yes' if user_data.differentially_abled else 'No'],
            ['Type of Disability', user_data.Type_of_disability if user_data.differentially_abled else 'N/A'],
            ['Special Quota', user_data.get_special_quota_display()],
            ['Permanent Address', str(user_data.permanent_address)],
            ['Communication Address', str(user_data.communication_address)]
        ]
        return Table(data)

    def generate_brief_details_table(self, brief_data):
        """Generate table for brief details"""
        data = [
            ['Brief Details'],
            ['Roll Number', str(brief_data.roll_number)],
            ['Identification Marks', brief_data.identification_marks],
            ['Extracurricular Activities', brief_data.extracurricular_activities],
            ['Brother Name', brief_data.brother_name],
            ['Brother Mobile', brief_data.brother_mobile],
            ['Sister Names', brief_data.sister_names or 'N/A'],
            ['Sister Mobile', brief_data.sister_mobile],
            ['Friends Names', brief_data.friends_names],
            ['Friends Mobile', brief_data.friends_mobile],
            ['Having Vehicle', 'Yes' if brief_data.having_vehicle else 'No'],
            ['Vehicle Number', brief_data.vehicle_number if brief_data.having_vehicle else 'N/A'],
            ['Health Issues', brief_data.any_health_issues],
            ['Hobbies', brief_data.hobbies]
        ]
        return Table(data)
    
        
    def generate_bank_details_table(self, bank_data):
        """Generate table for bank details"""
        data = [
            ['Bank Details'],
            ['Roll Number', str(bank_data.roll_number)],
            ['Account Holder', f"{bank_data.first_name} {bank_data.last_name}"],
            ['Account Number', str(bank_data.account_number)],
            ['Branch', bank_data.branch],
            ['IFSC Code', bank_data.ifsc],
            ['MICR Code', str(bank_data.micr)],
            ['Account Type', bank_data.account_type],
            ['Bank Address', bank_data.address],
            ['PAN Number', bank_data.pan_number]
        ]
        return Table(data)
    
    def generate_academics_details_table(self, aca_data):
        """Generate table for brief details"""
        data = [
            ['Academics Details'],
            ['Roll Number', str(aca_data.roll_number)],
            ['Course', aca_data.course],
            ['Department', aca_data.department],
            ['Current Year', aca_data.current_year],
            ['Current Semester', aca_data.current_semester],
            ['Year Joining', aca_data.year_joining],
            ['Type of Admission', aca_data.type_of_admission],
            ['Admission Type', aca_data.admission_type],
            ['EMIS Number', aca_data.emis_number],
            ['UMIS Number', aca_data.umis_number],
            ['Class Incharge', aca_data.class_incharge],
            ['Class Room Number', aca_data.class_room_number],

        ]
        return Table(data)
    
    def generate_ds_details_table(self, ds_data):
        """Generate table for brief details"""
        data = [
            ['Diploma Student Details'],
            ['Roll Number', str(ds_data.roll_number)],
            ['Diploma Register', ds_data.diploma_register],
            ['First Name', ds_data.first_name],
            ['Last Name', ds_data.last_name],
            ['SSLC Register', ds_data.sslc_register],
            ['HSC Register', ds_data.hsc_register if ds_data.hsc_register else 'N/A'],
            ['Course Name', ds_data.course_name],
            ['College Name', ds_data.college_name],
            ['Percentage', ds_data.percentage],
            ['Year of Joined', ds_data.year_of_joined],
            ['Year of Passed', ds_data.year_of_passed],
        ]
        return Table(data)
    
    def generate_sslc_details_table(self, sslc_data):
        """Generate table for brief details"""
        data = [
            ['SSLC Details'],
            ['Roll Number', str(sslc_data.roll_number)],
            ['SSLC Register', sslc_data.sslc_register],
            ['First Name', sslc_data.first_name],
            ['Last Name', sslc_data.last_name],
            ['School Name', sslc_data.school_name],
            ['School Address', sslc_data.school_address],
            ['Board', sslc_data.board],
            ['Marks Obtained', sslc_data.marks_obtained],
            ['SSLC Percentage', sslc_data.sslc_percentage],
            ['Passed Year', sslc_data.passed_year],
            ['EMIS Number', sslc_data.emis_number],

        ]
        return Table(data)
    
    def generate_hsc_details_table(self, hsc_data):
        """Generate table for brief details"""
        data = [
            ['HSC Details'],
            ['Roll Number', str(hsc_data.roll_number)],
            ['HSC Register', hsc_data.hsc_register],
            ['First Name', hsc_data.first_name],
            ['Last Name', hsc_data.last_name],
            ['School Name', hsc_data.school_name],
            ['School Address', hsc_data.school_address],
            ['Board', hsc_data.board],
            ['Marks Obtained', hsc_data.marks_obtained],
            ['SSLC Percentage', hsc_data.hsc_percentage],
            ['Passed Year', hsc_data.passed_year],
            ['EMIS Number', hsc_data.emis_number],

        ]
        return Table(data)
    
    def generate_rejoin_details_table(self, r_data):
        """Generate table for brief details"""
        data = [
            ['Rejoin Student Details'],
            ['Roll Number', str(r_data.roll_number)],
            ['New Roll Number', r_data.new_roll_number],
            ['Previous Type of Student', r_data.previous_type_of_student],
            ['Year of Discontinue', r_data.year_of_discontinue],
            ['Year of Rejoin', r_data.year_of_rejoin],
            ['Reason for Discontinue', r_data.reason_for_discontinue],
        ]
        return Table(data)
    
    def generate_host_details_table(self, host_data):
        """Generate table for brief details"""
        data = [
            ['Hostel Details'],
            ['Roll Number', str(host_data.roll_number)],
            ['First Name', host_data.first_name],
            ['Last Name', host_data.last_name],
            ['Hostel Name', host_data.hostel_name],
            ['Hostel Address', host_data.hostel_address],
            ['From Date', host_data.from_date],
            ['To Date', host_data.to_date],
            ['Room Number', host_data.room_number],

        ]
        return Table(data)
    def generate_scholarship_details_table(self, s_data):
        """Generate table for brief details"""
        data = [
            ['Scholarship Details'],
            ['Roll Number', str(s_data.roll_number)],
            ['Scholarship Type', s_data.scholarship_type],
            ['Academic Year Availed', s_data.academic_year_availed],
            ['Availed', s_data.availed],
        ]
        return Table(data)
    
    @method_decorator(csrf_exempt)
    def post(self, request):
        """Handle POST request to generate PDF"""
        session_id = request.COOKIES.get('session_id')
        if not session_id:
            return HttpResponse('Unauthorized', status=401)

        try:
            session = self.session_manager.get_session(session_id)
            if not session:
                raise jwt.InvalidTokenError()

            user = get_user_model().objects.get(id=session.user_id)
            selected_tables = request.POST.getlist('tables[]')
            
            if not selected_tables:
                return HttpResponse('Please select at least one table', status=400)

            # Create PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            
            # Add title
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30
            )
            elements.append(Paragraph("Department of Information Technology", title_style))
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("Student Details", title_style))
            elements.append(Spacer(1, 20))

            # Define table style
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ])

            # Get user data
            personal_info = PersonalInformation.objects.get(roll_number=user.username)

            # Add selected tables
            if 'personal' in selected_tables:
                table = self.generate_personal_info_table(personal_info)
                table.setStyle(table_style)
                elements.append(table)
                elements.append(Spacer(1, 20))

            if 'brief' in selected_tables:
                try:
                    brief_details = BriefDetails.objects.get(roll_number=personal_info)
                    table = self.generate_brief_details_table(brief_details)
                    table.setStyle(table_style)
                    elements.append(table)
                    elements.append(Spacer(1, 20))
                except BriefDetails.DoesNotExist:
                    elements.append(Paragraph("Brief Details not found", styles['Normal']))
                    elements.append(Spacer(1, 20))

            if 'bank' in selected_tables:
                try:
                    bank_details = BankDetails.objects.get(roll_number=personal_info)
                    table = self.generate_bank_details_table(bank_details)
                    table.setStyle(table_style)
                    elements.append(table)
                except BankDetails.DoesNotExist:
                    elements.append(Paragraph("Bank Details not found", styles['Normal']))

            if 'academics' in selected_tables:
                try:
                    aca_details = Academics.objects.get(roll_number=personal_info)
                    table = self.generate_academics_details_table(aca_details)
                    table.setStyle(table_style)
                    elements.append(table)
                    elements.append(Spacer(1, 20))
                except Academics.DoesNotExist:
                    elements.append(Paragraph("Academics Details not found", styles['Normal']))
                    elements.append(Spacer(1, 20))

            if 'sslc' in selected_tables:
                try:
                    sslc_details = SSLC.objects.get(roll_number=personal_info)
                    table = self.generate_sslc_details_table(sslc_details)
                    table.setStyle(table_style)
                    elements.append(table)
                    elements.append(Spacer(1, 20))
                except SSLC.DoesNotExist:
                    elements.append(Paragraph("SSLC Details not found", styles['Normal']))
                    elements.append(Spacer(1, 20))

            if 'hsc' in selected_tables:
                try:
                    hsc_details = HSC.objects.get(roll_number=personal_info)
                    table = self.generate_hsc_details_table(hsc_details)
                    table.setStyle(table_style)
                    elements.append(table)
                    elements.append(Spacer(1, 20))
                except HSC.DoesNotExist:
                    elements.append(Paragraph("HSC Details not found", styles['Normal']))
                    elements.append(Spacer(1, 20))

            if 'scholarship' in selected_tables:
                try:
                    s_details = Scholarship.objects.get(roll_number=personal_info)
                    table = self.generate_scholarship_details_table(s_details)
                    table.setStyle(table_style)
                    elements.append(table)
                    elements.append(Spacer(1, 20))
                except HSC.DoesNotExist:
                    elements.append(Paragraph("HSC Details not found", styles['Normal']))
                    elements.append(Spacer(1, 20))

            if 'hostellar' in selected_tables:
                try:
                    host_details = Hosteller.objects.get(roll_number=personal_info)
                    table = self.generate_host_details_table(host_details)
                    table.setStyle(table_style)
                    elements.append(table)
                    elements.append(Spacer(1, 20))
                except HSC.DoesNotExist:
                    elements.append(Paragraph("HSC Details not found", styles['Normal']))
                    elements.append(Spacer(1, 20))

            if 'ds' in selected_tables:
                try:
                    ds_details = DiplomaStudent.objects.get(roll_number=personal_info)
                    table = self.generate_ds_details_table(ds_details)
                    table.setStyle(table_style)
                    elements.append(table)
                    elements.append(Spacer(1, 20))
                except HSC.DoesNotExist:
                    elements.append(Paragraph("HSC Details not found", styles['Normal']))
                    elements.append(Spacer(1, 20))
            
            if 'rejoin' in selected_tables:
                try:
                    r_details = RejoinStudent.objects.get(roll_number=personal_info)
                    table = self.generate_rejoin_details_table(r_details)
                    table.setStyle(table_style)
                    elements.append(table)
                    elements.append(Spacer(1, 20))
                except HSC.DoesNotExist:
                    elements.append(Paragraph("HSC Details not found", styles['Normal']))
                    elements.append(Spacer(1, 20))





            # Build PDF
            doc.build(elements)
            buffer.seek(0)
            
            # Create response
            response = HttpResponse(buffer.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="student_details.pdf"'
            response['Content-Length'] = buffer.tell()
            response['HX-Trigger'] = 'pdfGenerated'
            
            return response

        except (jwt.InvalidTokenError, get_user_model().DoesNotExist):
            return HttpResponse('Unauthorized', status=401)
        except PersonalInformation.DoesNotExist:
            return HttpResponse('Student information not found', status=404)
        except Exception as e:
            return HttpResponse(f'Error generating PDF: {str(e)}', status=500)