#!/usr/bin/env python
"""
Production deployment script for Temple Attendance System
"""
import os
import sys
import subprocess

def run_command(command):
    """Run shell command and handle errors"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {command}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"✗ {command}")
        print(f"Error: {e.stderr}")
        sys.exit(1)

def deploy():
    """Deploy the application"""
    print("🚀 Starting Temple Attendance System deployment...")
    
    # Install production requirements
    run_command("pip install -r requirements-prod.txt")
    
    # Set production settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'temple_attendance.production_settings')
    
    # Run migrations
    run_command("python manage.py migrate")
    
    # Collect static files
    run_command("python manage.py collectstatic --noinput")
    
    # Create superuser if needed
    print("\n📝 Create superuser account:")
    run_command("python manage.py createsuperuser")
    
    print("\n✅ Deployment completed successfully!")
    print("🌐 Your Temple Attendance System is ready for production!")

if __name__ == "__main__":
    deploy()