from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import date, time, timedelta
from attendance.models import Devotee, Sabha, Attendance

class Command(BaseCommand):
    help = 'Seed database with sample data'

    def handle(self, *args, **options):
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@temple.com', 'admin123')
            self.stdout.write('Created admin user (username: admin, password: admin123)')

        # Create sample devotees
        devotees_data = [
            {'name': 'Ravi Patel', 'contact_number': '9876543210', 'age_group': '25-35', 'sabha_type': 'yuvak', 'address': '123 Temple Street', 'join_date': date(2023, 1, 15)},
            {'name': 'Priya Shah', 'contact_number': '9876543211', 'age_group': '20-30', 'sabha_type': 'mahila', 'address': '456 Devotee Lane', 'join_date': date(2023, 2, 10)},
            {'name': 'Arjun Kumar', 'contact_number': '9876543212', 'age_group': '8-12', 'sabha_type': 'bal', 'address': '789 Sabha Road', 'join_date': date(2023, 3, 5)},
            {'name': 'Meera Desai', 'contact_number': '9876543213', 'age_group': '35-45', 'sabha_type': 'mahila', 'address': '321 Temple Avenue', 'join_date': date(2023, 1, 20)},
            {'name': 'Kiran Joshi', 'contact_number': '9876543214', 'age_group': '18-25', 'sabha_type': 'yuvak', 'address': '654 Bhakti Street', 'join_date': date(2023, 4, 1)},
        ]

        for devotee_data in devotees_data:
            devotee, created = Devotee.objects.get_or_create(
                name=devotee_data['name'],
                defaults=devotee_data
            )
            if created:
                self.stdout.write(f'Created devotee: {devotee.name}')

        # Create sample sabhas
        today = date.today()
        sabhas_data = [
            {'date': today - timedelta(days=7), 'sabha_type': 'bal', 'location': 'Main Hall', 'start_time': time(10, 0), 'end_time': time(11, 30)},
            {'date': today - timedelta(days=6), 'sabha_type': 'yuvak', 'location': 'Youth Center', 'start_time': time(18, 0), 'end_time': time(19, 30)},
            {'date': today - timedelta(days=5), 'sabha_type': 'mahila', 'location': 'Community Hall', 'start_time': time(16, 0), 'end_time': time(17, 30)},
            {'date': today, 'sabha_type': 'general', 'location': 'Main Temple', 'start_time': time(19, 0), 'end_time': time(20, 30)},
            {'date': today + timedelta(days=1), 'sabha_type': 'bal', 'location': 'Main Hall', 'start_time': time(10, 0), 'end_time': time(11, 30)},
        ]

        for sabha_data in sabhas_data:
            sabha, created = Sabha.objects.get_or_create(
                date=sabha_data['date'],
                sabha_type=sabha_data['sabha_type'],
                defaults=sabha_data
            )
            if created:
                self.stdout.write(f'Created sabha: {sabha}')

        # Create sample attendance records
        past_sabhas = Sabha.objects.filter(date__lt=today)
        for sabha in past_sabhas:
            devotees = Devotee.objects.filter(sabha_type=sabha.sabha_type)
            for devotee in devotees:
                attendance, created = Attendance.objects.get_or_create(
                    devotee=devotee,
                    sabha=sabha,
                    defaults={'status': 'present', 'notes': 'Sample attendance'}
                )
                if created:
                    self.stdout.write(f'Created attendance: {attendance}')

        self.stdout.write(self.style.SUCCESS('Successfully seeded database with sample data!'))