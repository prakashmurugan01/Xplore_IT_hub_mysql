import importlib
from io import BytesIO
from datetime import datetime, date
from django.http import HttpResponse
from django.db.models import Avg, Count, Q
from django.core.exceptions import PermissionDenied


class TeacherReportGenerator:
    """
    Advanced teacher performance and analytics report generator with comprehensive metrics,
    visual enhancements, and robust error handling.
    """
    
    def __init__(self, teacher_profile, request=None):
        self.teacher = teacher_profile
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
        story.append(Paragraph('Teacher Performance Report', subtitle_style))
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

    def _create_teacher_info_section(self, story, components):
        """Create enhanced teacher information section with photo."""
        from .models import Course
        
        Table = components['platypus'].Table
        TableStyle = components['platypus'].TableStyle
        Paragraph = components['platypus'].Paragraph
        Spacer = components['platypus'].Spacer
        Image = components['platypus'].Image
        colors = components['colors']
        inch = components['units'].inch
        
        # Section header
        section_style = self._create_section_header_style(components)
        story.append(Paragraph('Teacher Information', section_style))
        story.append(Spacer(1, 0.15*inch))
        
        # Gather teacher data with safe attribute access
        join_date = 'N/A'
        try:
            if hasattr(self.teacher.user, 'date_joined') and self.teacher.user.date_joined:
                join_date = self.teacher.user.date_joined.strftime('%B %d, %Y')
        except Exception:
            pass
        
        # Count courses
        course_count = Course.objects.filter(teacher=self.teacher).count()
        
        teacher_data = [
            ['Full Name:', self.teacher.user.get_full_name() or self.teacher.user.username or 'N/A'],
            ['Username:', self.teacher.user.username or 'N/A'],
            ['Email:', self.teacher.user.email or 'Not provided'],
            ['Phone:', getattr(self.teacher, 'phone', 'Not provided') or 'Not provided'],
            ['Department:', getattr(self.teacher, 'department', 'Not assigned') or 'Not assigned'],
            ['Specialization:', getattr(self.teacher, 'specialization', 'Not specified') or 'Not specified'],
            ['Joined:', join_date],
            ['Active Courses:', str(course_count)],
        ]
        
        # Create teacher info table
        teacher_table = Table(teacher_data, colWidths=[1.6*inch, 3.4*inch])
        teacher_table.setStyle(TableStyle([
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
                [[teacher_table, photo_flowable]], 
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
            story.append(teacher_table)
        
        story.append(Spacer(1, 0.4*inch))

    def _get_profile_photo(self, components):
        """Safely retrieve and format profile photo."""
        Image = components['platypus'].Image
        Paragraph = components['platypus'].Paragraph
        Table = components['platypus'].Table
        TableStyle = components['platypus'].TableStyle
        colors = components['colors']
        inch = components['units'].inch
        
        if not getattr(self.teacher, 'profile_pic', None):
            return None
        
        try:
            img_path = getattr(self.teacher.profile_pic, 'path', None)
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
            elif self.request and getattr(self.teacher.profile_pic, 'url', None):
                photo_url = self.request.build_absolute_uri(self.teacher.profile_pic.url)
                return Paragraph(
                    f'<font size="8">Photo: <a href="{photo_url}" color="blue">View Online</a></font>',
                    self.styles['Normal']
                )
        except Exception as e:
            print(f"Error loading profile photo: {e}")
        
        return None

    def _create_course_section(self, story, components):
        """Create comprehensive course analytics section."""
        from .models import Course, Enrollment, Attendance
        
        Paragraph = components['platypus'].Paragraph
        Spacer = components['platypus'].Spacer
        Table = components['platypus'].Table
        TableStyle = components['platypus'].TableStyle
        colors = components['colors']
        inch = components['units'].inch
        
        section_style = self._create_section_header_style(components)
        story.append(Paragraph('Course Summary', section_style))
        story.append(Spacer(1, 0.15*inch))
        
        courses = Course.objects.filter(teacher=self.teacher)
        
        if not courses.exists():
            story.append(Paragraph('No courses assigned.', self.styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            return
        
        course_data = [['Course Code', 'Course Name', 'Students', 'Classes', 'Avg. Attendance', 'Performance']]
        
        total_students = 0
        total_classes = 0
        overall_attendance = 0
        course_count = 0
        
        for course in courses:
            student_count = Enrollment.objects.filter(course=course).count()
            class_count = Attendance.objects.filter(course=course).values('date').distinct().count()
            
            # Calculate average attendance
            total_attendance = Attendance.objects.filter(
                course=course,
                status=True
            ).count()
            total_possible = student_count * class_count if student_count and class_count else 0
            attendance_rate = (total_attendance / total_possible * 100) if total_possible > 0 else 0
            
            total_students += student_count
            total_classes += class_count
            overall_attendance += attendance_rate
            course_count += 1
            
            # Performance indicator based on attendance and other metrics
            if attendance_rate >= 75 and student_count >= 10:
                performance = 'Excellent'
            elif attendance_rate >= 60 or student_count >= 5:
                performance = 'Good'
            else:
                performance = 'Needs Attention'
            
            course_data.append([
                course.code or 'N/A',
                course.name[:25] if len(course.name) > 25 else course.name,
                str(student_count),
                str(class_count),
                f"{attendance_rate:.1f}%",
                performance
            ])
        
        # Add overall summary row
        avg_attendance = overall_attendance / course_count if course_count > 0 else 0
        avg_students = total_students / course_count if course_count > 0 else 0
        
        course_data.append([
            '', 
            'OVERALL', 
            f"{total_students} ({avg_students:.1f}/course)", 
            str(total_classes),
            f"{avg_attendance:.1f}%",
            self._get_overall_performance(avg_attendance, avg_students)
        ])
        
        course_table = Table(
            course_data, 
            colWidths=[1*inch, 2*inch, 1*inch, 0.8*inch, 1.1*inch, 1.1*inch]
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
        for i in range(1, len(course_data) - 1):
            bg_color = colors.white if i % 2 == 1 else colors.HexColor('#f9fafb')
            table_style.append(('BACKGROUND', (0, i), (-1, i), bg_color))
        
        course_table.setStyle(TableStyle(table_style))
        story.append(course_table)
        story.append(Spacer(1, 0.4*inch))

    def _get_overall_performance(self, avg_attendance, avg_students):
        """Calculate overall performance rating."""
        if avg_attendance >= 75 and avg_students >= 10:
            return 'Outstanding'
        elif avg_attendance >= 60 or avg_students >= 5:
            return 'Satisfactory'
        else:
            return 'Needs Improvement'

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
        self._create_teacher_info_section(story, components)
        self._create_course_section(story, components)
        self._create_footer(story, components)
        
        # Generate PDF
        doc.build(story)
        pdf = self.buffer.getvalue()
        self.buffer.close()
        
        return pdf


def download_teacher_report(request):
    """
    View function to generate and download teacher performance report.
    Restricted to authenticated teachers only.
    """
    # Verify user is authenticated
    if not request.user.is_authenticated:
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(request, 'Please login to access your report.')
        return redirect('login')
    
    # Verify user has teacher role
    profile = getattr(request.user, 'profile', None)
    if not profile or getattr(profile, 'role', None) != 'teacher':
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, 'Access denied! This feature is only available to teachers.')
        return redirect('role_redirect')
    
    try:
        # Generate report
        generator = TeacherReportGenerator(profile, request=request)
        pdf = generator.generate_report()
        
        # Create response
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"teacher_report_{request.user.username}_{timestamp}.pdf"
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(pdf)
        
        return response
        
    except Exception as e:
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, f'Error generating report: {str(e)}')
        return redirect('teacher_dashboard')