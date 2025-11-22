from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from .mongodb_models import AdminUserManager

class MongoDBAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        admin_manager = AdminUserManager()
        admin_user = admin_manager.authenticate(username, password)
        
        if admin_user:
            # Create or get Django user for session management
            django_user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': admin_user.email or '', 'is_active': True}
            )
            if not created:
                django_user.email = admin_user.email or ''
                django_user.is_active = True
                django_user.save()
            
            # Set superuser status for admin users
            if admin_user.is_admin:
                django_user.is_superuser = True
                django_user.is_staff = True
                django_user.save()
            
            return django_user
        
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None