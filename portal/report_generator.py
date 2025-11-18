import importlib
from io import BytesIO
from datetime import datetime
from django.http import HttpResponse
from django.db.models import Avg, Count, Q
from django.core.exceptions import PermissionDenied


class EnhancedStudentReportGenerator:
    """
    Professional student performance report generator with comprehensive metrics,
    visual enhancements, and robust error handling.
    """
    
    def __init__(self, student_profile, request=None):
        self.student = student_profile
        self.request = request
        self.buffer = BytesIO()
        self.styles = None
        self.colors = None
        self.current_date = datetime.now().strftime('%B %d, %Y')
        
    def _import_reportlab(self):
        """Dynamically import reportlab components with error handling."""
        try:
            modules = {
                'pagesizes': importlib.import_module('reportlab.lib.pagesizes'),
                'colors': importlib.import_module('reportlab.lib.colors'),
                'units': importlib.import_module('reportlab.lib.units'),
                'platypus': importlib.import_module('reportlab.platypus'),
                'styles_mod': importlib.import_module('reportlab.lib.styles'),
                'enums': importlib.import_module('reportlab.lib.enums'),
            }
            return modules
        except ImportError as e:
            raise RuntimeError(
                f'ReportLab is required for PDF generation. Install it with: pip install reportlab. Error: {e}'
            )
    
    def _create_header(self, story, components):
        """Create professional report header with institution branding."""
        Paragraph = components['platypus'].Paragraph
        Spacer = components['platypus'].Spacer
        Table = components['platypus'].Table
        TableStyle = components['platypus'].TableStyle
        colors = components['colors']
        inch = components['units'].inch
        ParagraphStyle = components['styles_mod'].ParagraphStyle
        TA_CENTER = components['enums'].TA_CENTER
        TA_RIGHT = components['enums'].TA_RIGHT
        
        # Institution title with modern styling
        title_style = ParagraphStyle(
            'InstitutionTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1a56db'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#4b5563'),
            spaceAfter=4,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        date_style = ParagraphStyle(
            'DateStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#6b7280'),
            alignment=TA_RIGHT,
            fontName='Helvetica'
        )
        
        story.append(Paragraph('XPLORE IT HUB', title_style))
        story.append(Paragraph('Student Performance Report', subtitle_style))
        story.append(Paragraph(f'Generated on: {self.current_date}', date_style))
        story.append(Spacer(1, 0.4*inch))
        
        # Decorative line
        line_table = Table([['']], colWidths=[7*inch])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 3, colors.HexColor('#1a56db')),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#93c5fd')),
        ]))
        story.append(line_table)
        story.append(Spacer(1, 0.3*inch))
    
    def _create_student_info_section(self, story, components):
        """Create enhanced student information section with photo."""
        from .models import Enrollment
        
        Table = components['platypus'].Table
        TableStyle = components['platypus'].TableStyle
        Paragraph = components['platypus'].Paragraph
        Spacer = components['platypus'].Spacer
        Image = components['platypus'].Image
        colors = components['colors']
        inch = components['units'].inch
        
        # Section header
        section_style = self._create_section_header_style(components)
        story.append(Paragraph('Student Information', section_style))
        story.append(Spacer(1, 0.15*inch))
        
        # Gather student data with safe attribute access
        join_date = 'N/A'
        try:
            if hasattr(self.student.user, 'date_joined') and self.student.user.date_joined:
                join_date = self.student.user.date_joined.strftime('%B %d, %Y')
        except Exception:
            pass
        
        # Count enrollments
        enrollment_count = Enrollment.objects.filter(student=self.student).count()
        
        student_data = [
            ['Full Name:', self.student.user.get_full_name() or self.student.user.username or 'N/A'],
            ['Username:', self.student.user.username or 'N/A'],
            ['Email:', self.student.user.email or 'Not provided'],
            ['Phone:', getattr(self.student, 'phone', 'Not provided') or 'Not provided'],
            ['Department:', getattr(self.student, 'department', 'Not assigned') or 'Not assigned'],
            ['Role:', (getattr(self.student, 'role', 'student') or 'student').title()],
            ['Joined:', join_date],
            ['Enrolled Courses:', str(enrollment_count)],
        ]
        
        # Create student info table
        student_table = Table(student_data, colWidths=[1.6*inch, 3.4*inch])
        student_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1a56db')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f3f4f6')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        # Handle profile photo
        photo_flowable = self._get_profile_photo(components)
        
        if photo_flowable:
            combined = Table(
                [[student_table, photo_flowable]], 
                colWidths=[5*inch, 2*inch]
            )
            combined.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ]))
            story.append(combined)
        else:
            story.append(student_table)
        
        story.append(Spacer(1, 0.4*inch))
    
    def _get_profile_photo(self, components):
        """Safely retrieve and format profile photo."""
        Image = components['platypus'].Image
        Paragraph = components['platypus'].Paragraph
        Table = components['platypus'].Table
        TableStyle = components['platypus'].TableStyle
        colors = components['colors']
        inch = components['units'].inch
        
        if not getattr(self.student, 'profile_pic', None):
            return None
        
        try:
            img_path = getattr(self.student.profile_pic, 'path', None)
            if img_path:
                img = Image(img_path)
                aspect = img.imageHeight / img.imageWidth
                img.drawWidth = 1.5*inch
                img.drawHeight = 1.5*inch * aspect
                
                # Wrap image in a table with border
                img_table = Table([[img]], colWidths=[1.5*inch])
                img_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                    ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1a56db')),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                return img_table
            elif self.request and getattr(self.student.profile_pic, 'url', None):
                photo_url = self.request.build_absolute_uri(self.student.profile_pic.url)
                return Paragraph(
                    f'<font size="8">Photo: <a href="{photo_url}" color="blue">View Online</a></font>',
                    self.styles['Normal']
                )
        except Exception as e:
            print(f"Error loading profile photo: {e}")
        
        return None
    
    def _create_attendance_section(self, story, components):
        """Create comprehensive attendance analytics section."""
        from .models import Enrollment, Attendance
        
        Paragraph = components['platypus'].Paragraph
        Spacer = components['platypus'].Spacer
        Table = components['platypus'].Table
        TableStyle = components['platypus'].TableStyle
        colors = components['colors']
        inch = components['units'].inch
        
        section_style = self._create_section_header_style(components)
        story.append(Paragraph('Attendance Summary', section_style))
        story.append(Spacer(1, 0.15*inch))
        
        enrollments = Enrollment.objects.filter(student=self.student).select_related('course')
        
        if not enrollments.exists():
            story.append(Paragraph('No course enrollments found.', self.styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            return
        
        attendance_data = [['Course Code', 'Course Name', 'Total', 'Present', 'Absent', 'Attendance %']]
        
        total_classes = 0
        total_present = 0
        
        for enrollment in enrollments:
            course = enrollment.course
            total = Attendance.objects.filter(
                student=self.student, 
                course=course
            ).count()
            present = Attendance.objects.filter(
                student=self.student, 
                course=course, 
                status=True
            ).count()
            absent = total - present
            percentage = (present / total * 100) if total > 0 else 0
            
            total_classes += total
            total_present += present
            
            # Color code attendance percentage
            perc_display = f"{percentage:.1f}%"
            
            attendance_data.append([
                course.code or 'N/A',
                course.name[:25] if len(course.name) > 25 else course.name,
                str(total),
                str(present),
                str(absent),
                perc_display
            ])
        
        # Add overall summary row
        overall_percentage = (total_present / total_classes * 100) if total_classes > 0 else 0
        attendance_data.append([
            '', 
            'OVERALL', 
            str(total_classes), 
            str(total_present), 
            str(total_classes - total_present),
            f"{overall_percentage:.1f}%"
        ])
        
        attendance_table = Table(
            attendance_data, 
            colWidths=[1*inch, 2.2*inch, 0.8*inch, 0.9*inch, 0.8*inch, 1.3*inch]
        )
        
        # Apply styling with color-coded rows
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#dbeafe')),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#059669')),
        ]
        
        # Alternate row colors for better readability
        for i in range(1, len(attendance_data) - 1):
            bg_color = colors.white if i % 2 == 1 else colors.HexColor('#f9fafb')
            table_style.append(('BACKGROUND', (0, i), (-1, i), bg_color))
        
        attendance_table.setStyle(TableStyle(table_style))
        story.append(attendance_table)
        
        # Add attendance performance note
        if overall_percentage >= 75:
            note = f'<font color="green">✓ Excellent attendance rate of {overall_percentage:.1f}%</font>'
        elif overall_percentage >= 60:
            note = f'<font color="orange">⚠ Moderate attendance rate of {overall_percentage:.1f}%. Improvement recommended.</font>'
        else:
            note = f'<font color="red">✗ Low attendance rate of {overall_percentage:.1f}%. Immediate attention required.</font>'
        
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(note, self.styles['Normal']))
        story.append(Spacer(1, 0.4*inch))
    
    def _create_assignment_section(self, story, components):
        """Create detailed assignment performance section."""
        from .models import Submission
        
        Paragraph = components['platypus'].Paragraph
        Spacer = components['platypus'].Spacer
        Table = components['platypus'].Table
        TableStyle = components['platypus'].TableStyle
        colors = components['colors']
        inch = components['units'].inch
        
        section_style = self._create_section_header_style(components)
        story.append(Paragraph('Assignment Performance', section_style))
        story.append(Spacer(1, 0.15*inch))
        
        submissions = Submission.objects.filter(
            student=self.student
        ).exclude(
            marks_obtained__isnull=True
        ).select_related('assignment', 'assignment__course')
        
        if not submissions.exists():
            story.append(Paragraph('No graded assignments found.', self.styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            return
        
        perf_data = [['Assignment', 'Course', 'Max Marks', 'Obtained', 'Score %', 'Grade']]
        
        total_percentage = 0
        count = 0
        
        for sub in submissions:
            assignment = sub.assignment
            max_marks = assignment.max_marks or 100
            obtained = sub.marks_obtained or 0
            percentage = (obtained / max_marks * 100) if max_marks else 0
            grade = self._calculate_grade(percentage)
            
            total_percentage += percentage
            count += 1
            
            perf_data.append([
                assignment.title[:30],
                assignment.course.code or assignment.course.name[:15],
                str(int(max_marks)),
                str(int(obtained)),
                f"{percentage:.1f}%",
                grade
            ])
        
        # Calculate statistics
        avg_percentage = total_percentage / count if count > 0 else 0
        avg_grade = self._calculate_grade(avg_percentage)
        
        # Add summary row
        perf_data.append([
            '', 
            'AVERAGE', 
            '', 
            '', 
            f"{avg_percentage:.1f}%",
            avg_grade
        ])
        
        perf_table = Table(
            perf_data, 
            colWidths=[2*inch, 1.2*inch, 1*inch, 1*inch, 0.9*inch, 0.9*inch]
        )
        
        # Enhanced styling
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('ALIGN', (0, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#dbeafe')),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#f59e0b')),
        ]
        
        # Alternate row colors
        for i in range(1, len(perf_data) - 1):
            bg_color = colors.white if i % 2 == 1 else colors.HexColor('#fffbeb')
            table_style.append(('BACKGROUND', (0, i), (-1, i), bg_color))
        
        perf_table.setStyle(TableStyle(table_style))
        story.append(perf_table)
        
        # Performance summary
        story.append(Spacer(1, 0.1*inch))
        if avg_percentage >= 80:
            note = f'<font color="green">✓ Outstanding performance with {avg_percentage:.1f}% average</font>'
        elif avg_percentage >= 60:
            note = f'<font color="orange">⚠ Satisfactory performance with {avg_percentage:.1f}% average</font>'
        else:
            note = f'<font color="red">✗ Needs improvement with {avg_percentage:.1f}% average</font>'
        
        story.append(Paragraph(note, self.styles['Normal']))
        story.append(Spacer(1, 0.4*inch))
    
    def _create_footer(self, story, components):
        """Create professional footer with signature line."""
        Paragraph = components['platypus'].Paragraph
        Spacer = components['platypus'].Spacer
        Table = components['platypus'].Table
        TableStyle = components['platypus'].TableStyle
        colors = components['colors']
        inch = components['units'].inch
        
        story.append(Spacer(1, 0.5*inch))
        
        # Decorative line
        line_table = Table([['']], colWidths=[7*inch])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#d1d5db')),
        ]))
        story.append(line_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Footer content
        footer_text = f'''
        <para alignment="center">
        <font size="8" color="#6b7280">
        This is a computer-generated report from XPLORE IT HUB.<br/>
        Generated on {self.current_date} | For academic use only<br/>
        © {datetime.now().year} XPLORE IT HUB. All rights reserved.
        </font>
        </para>
        '''
        story.append(Paragraph(footer_text, self.styles['Normal']))
    
    def _create_section_header_style(self, components):
        """Create consistent section header styling."""
        ParagraphStyle = components['styles_mod'].ParagraphStyle
        colors = components['colors']
        
        return ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=0,
            spaceBefore=0,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=colors.HexColor('#1a56db'),
            borderPadding=6,
            backColor=colors.HexColor('#eff6ff')
        )
    
    def _calculate_grade(self, percentage):
        """Calculate letter grade from percentage."""
        if percentage >= 90:
            return 'A+'
        elif percentage >= 80:
            return 'A'
        elif percentage >= 70:
            return 'B+'
        elif percentage >= 60:
            return 'B'
        elif percentage >= 50:
            return 'C'
        elif percentage >= 40:
            return 'D'
        else:
            return 'F'
    
    def generate_report(self):
        """Generate the complete PDF report."""
        # Import reportlab components
        components = self._import_reportlab()
        
        A4 = components['pagesizes'].A4
        SimpleDocTemplate = components['platypus'].SimpleDocTemplate
        getSampleStyleSheet = components['styles_mod'].getSampleStyleSheet
        
        # Initialize styles
        self.styles = getSampleStyleSheet()
        self.colors = components['colors']
        
        # Create document
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=0.75 * components['units'].inch,
            leftMargin=0.75 * components['units'].inch,
            topMargin=0.75 * components['units'].inch,
            bottomMargin=0.75 * components['units'].inch
        )
        
        story = []
        
        # Build report sections
        self._create_header(story, components)
        self._create_student_info_section(story, components)
        self._create_attendance_section(story, components)
        self._create_assignment_section(story, components)
        self._create_footer(story, components)
        
        # Generate PDF
        doc.build(story)
        pdf = self.buffer.getvalue()
        self.buffer.close()
        
        return pdf


def download_student_report(request):
    """
    View function to generate and download student performance report.
    Restricted to authenticated students only.
    """
    # Verify user is authenticated
    if not request.user.is_authenticated:
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(request, 'Please login to access your report.')
        return redirect('login')
    
    # Verify user has student role
    profile = getattr(request.user, 'profile', None)
    if not profile or getattr(profile, 'role', None) != 'student':
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, 'Access denied! This feature is only available to students.')
        return redirect('role_redirect')
    
    try:
        # Generate report
        generator = EnhancedStudentReportGenerator(profile, request=request)
        pdf = generator.generate_report()
        
        # Create response
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"student_report_{request.user.username}_{timestamp}.pdf"
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(pdf)
        
        return response
        
    except Exception as e:
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, f'Error generating report: {str(e)}')
        return redirect('student_dashboard')


# Backwards-compatible alias expected by other modules
StudentReportGenerator = EnhancedStudentReportGenerator