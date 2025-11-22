from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from admin_panel.mongodb_models import AdminUserManager
from attendance.models import UserProfile

class Command(BaseCommand):
    help = 'Create an admin user with full permissions'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Admin username', default='admin')
        parser.add_argument('--email', type=str, help='Admin email', default='admin@temple.com')
        parser.add_argument('--password', type=str, help='Admin password', default='admin123')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        
        try:
            # Create Django superuser
            if User.objects.filter(username=username).exists():
                self.stdout.write(f'Django user {username} already exists')
            else:
                django_user = User.objects.create_superuser(username=username, email=email, password=password)
                self.stdout.write(f'Created Django superuser: {username}')
            
            # Create UserProfile with all sabha types
            django_user = User.objects.get(username=username)
            profile, created = UserProfile.objects.get_or_create(user=django_user)
            profile.allowed_sabha_types = ['bal', 'yuvak', 'mahila', 'sanyukt']
            profile.save()
            
            # Create admin user in MongoDB
            admin_manager = AdminUserManager()
            if admin_manager.get_user_by_username(username):
                self.stdout.write(f'Admin user {username} already exists in MongoDB')
            else:
                admin_manager.create_user(
                    username=username,
                    email=email,
                    password=password,
                    allowed_sabha_types=['bal', 'yuvak', 'mahila', 'sanyukt'],
                    is_admin=True
                )
                self.stdout.write(f'Created admin user in MongoDB: {username}')
            
            self.stdout.write(
                self.style.SUCCESS(f'Admin user setup complete!\nUsername: {username}\nPassword: {password}')
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating admin user: {str(e)}'))