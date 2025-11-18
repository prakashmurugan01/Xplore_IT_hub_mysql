from django import forms
from django.contrib.auth.models import User
from .models import Profile
from .models import Schedule, Course


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = [
            'title', 'description', 'date', 'start_time', 'end_time', 'location', 'course',
            'is_public', 'is_recurring', 'recurrence_rule', 'notify_students', 'reminder_minutes', 'attachment', 'color'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class StudentCreateForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = Profile
        fields = ['student_class', 'roll_number', 'phone', 'department']

    def save(self, commit=True):
        # Create or update the related User
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        email = self.cleaned_data.get('email')
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')

        # If instance has a user, update it; else create
        if self.instance and getattr(self.instance, 'user', None):
            user = self.instance.user
            user.username = username
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            if password:
                user.set_password(password)
            if commit:
                user.save()
        else:
            user = User.objects.create_user(username=username, email=email, password=password or 'password')
            user.first_name = first_name
            user.last_name = last_name
            if commit:
                user.save()

            # Some projects auto-create Profile via a post_save signal when a User is created.
            # If that's the case, reuse that Profile instead of attempting to insert a duplicate.
            try:
                existing_profile = getattr(user, 'profile', None)
            except Exception:
                existing_profile = None

            if existing_profile:
                profile = existing_profile
                # update profile fields from form
                profile.student_class = self.cleaned_data.get('student_class')
                profile.roll_number = self.cleaned_data.get('roll_number')
                profile.phone = self.cleaned_data.get('phone')
                profile.department = self.cleaned_data.get('department')
                profile.role = 'student'
                if commit:
                    profile.save()
                self.instance = profile
            else:
                self.instance.user = user

        profile = super().save(commit=False)
        profile.role = 'student'
        if commit:
            profile.save()
        return profile
