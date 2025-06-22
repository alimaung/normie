from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from normieapp.models import UserProfile


class Command(BaseCommand):
    help = 'Create an admin user with full permissions'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Admin username', default='admin')
        parser.add_argument('--email', type=str, help='Admin email', default='admin@normie.de')
        parser.add_argument('--password', type=str, help='Admin password', default='admin123')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists.')
            )
            return

        # Create the user
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        # Create or update the profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.role = 'admin'
        profile.department = 'IT Administration'
        profile.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created admin user "{username}" with password "{password}"'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'User has been assigned the "admin" role with full permissions.'
            )
        ) 