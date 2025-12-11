"""
Django management command to create a superadmin user.
Usage: python manage.py create_superadmin
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create a Django superadmin user interactively'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Superadmin username',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Superadmin email address',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Superadmin password (will prompt if not provided)',
        )
        parser.add_argument(
            '--noinput',
            action='store_true',
            help='Run without prompts (requires all args)',
        )

    def handle(self, *args, **options):
        username = options.get('username')
        email = options.get('email')
        password = options.get('password')
        noinput = options.get('noinput', False)

        # If noinput, all args are required
        if noinput:
            if not username or not email or not password:
                self.stdout.write(
                    self.style.ERROR(
                        'Error: --username, --email, and --password are required when using --noinput'
                    )
                )
                return

        # Prompt for missing values
        if not username:
            username = input('Superadmin username: ').strip()
            if not username:
                self.stdout.write(self.style.ERROR('Username cannot be empty'))
                return

        if not email:
            email = input('Superadmin email: ').strip()
            if not email:
                self.stdout.write(self.style.ERROR('Email cannot be empty'))
                return

        if not password:
            import getpass
            password = getpass.getpass('Superadmin password: ')
            if not password:
                self.stdout.write(self.style.ERROR('Password cannot be empty'))
                return

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists. Skipping.')
            )
            return

        # Create superuser
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Superadmin user "{username}" created successfully!'
                )
            )
            self.stdout.write(f'  Username: {user.username}')
            self.stdout.write(f'  Email: {user.email}')
            self.stdout.write(f'  URL: http://127.0.0.1:8000/admin/')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating superadmin: {e}'))
