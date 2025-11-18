from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
import getpass

User = get_user_model()

class Command(BaseCommand):
    help = 'Promote an existing user to superadmin or admin2 (sets profile.role, is_staff, is_superuser). Optionally creates the user.'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to promote or create')
        # Accept any role string but validate at runtime against Profile.ROLE_CHOICES
        try:
            from portal.models import Profile
            allowed = [r[0] for r in Profile.ROLE_CHOICES]
        except Exception:
            allowed = ['superadmin', 'admin2', 'teacher', 'student', 'finance', 'staff']
        parser.add_argument('--role', type=str, default='superadmin', help=f"Role to assign (one of: {', '.join(allowed)})")
        parser.add_argument('--create', action='store_true', help='Create the user if it does not exist')
        parser.add_argument('--email', type=str, help='Email for created user')
        parser.add_argument('--password', type=str, help='Password for created user (if not provided will prompt)')

    @transaction.atomic
    def handle(self, *args, **options):
        username = options['username']
        role = options['role']
        create = options['create']
        email = options.get('email') or ''
        password = options.get('password')

        try:
            user = User.objects.get(username=username)
            created = False
        except User.DoesNotExist:
            if not create:
                raise CommandError(f"User '{username}' does not exist. Use --create to create it.")
            # create the user
            if not password:
                password = getpass.getpass(prompt='Password for new user: ')
            user = User.objects.create_user(username=username, email=email, password=password)
            created = True

        # ensure a profile exists
        if not hasattr(user, 'profile') or user.profile is None:
            from portal.models import Profile
            # create profile if missing
            Profile.objects.get_or_create(user=user)

        # set role (validate against Profile.ROLE_CHOICES when possible)
        try:
            try:
                from portal.models import Profile
                allowed = {r[0] for r in Profile.ROLE_CHOICES}
            except Exception:
                allowed = {'superadmin', 'admin2', 'teacher', 'student', 'finance', 'staff'}
            if role not in allowed:
                raise CommandError(f"Role '{role}' is not valid. Allowed: {', '.join(sorted(allowed))}")

            user.profile.role = role
            user.profile.save()
        except Exception as e:
            raise CommandError(f'Failed to set profile.role: {e}')

        # give Django admin access for superadmin
        if role == 'superadmin':
            user.is_staff = True
            user.is_superuser = True
        else:
            # admin2 gets staff but not superuser by default
            user.is_staff = True
            user.is_superuser = False
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created user '{username}' with role '{role}'"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Updated user '{username}' -> role '{role}' (is_staff={user.is_staff}, is_superuser={user.is_superuser})"))
