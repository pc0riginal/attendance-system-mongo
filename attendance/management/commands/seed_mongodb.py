from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from attendance.mongodb_utils import MongoDBManager

class Command(BaseCommand):
    help = 'Seed MongoDB with sample data'

    def handle(self, *args, **options):
        # Initialize MongoDB managers
        devotees_db = MongoDBManager('devotees')
        sabhas_db = MongoDBManager('sabhas')
        attendance_db = MongoDBManager('attendance_records')

        # Create admin user
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@temple.com', 'admin123')
            self.stdout.write('Created admin user (username: admin, password: admin123)')

        # Create sample devotees
        devotees_data = [
            {
                'name': 'Ravi Patel',
                'contact_number': '9876543210',
                'age_group': '25-35',
                'sabha_type': 'yuvak',
                'address': '123 Temple Street',
                'join_date': '2023-01-15',
                'photo_url': 'https://via.placeholder.com/150',
                'created_at': datetime.now().isoformat()
            },
            {
                'name': 'Priya Shah',
                'contact_number': '9876543211',
                'age_group': '20-30',
                'sabha_type': 'mahila',
                'address': '456 Devotee Lane',
                'join_date': '2023-02-10',
                'photo_url': 'https://via.placeholder.com/150',
                'created_at': datetime.now().isoformat()
            },
            {
                'name': 'Arjun Kumar',
                'contact_number': '9876543212',
                'age_group': '8-12',
                'sabha_type': 'bal',
                'address': '789 Sabha Road',
                'join_date': '2023-03-05',
                'photo_url': 'https://via.placeholder.com/150',
                'created_at': datetime.now().isoformat()
            },
            {
                'name': 'Meera Desai',
                'contact_number': '9876543213',
                'age_group': '35-45',
                'sabha_type': 'mahila',
                'address': '321 Temple Avenue',
                'join_date': '2023-01-20',
                'photo_url': 'https://via.placeholder.com/150',
                'created_at': datetime.now().isoformat()
            },
            {
                'name': 'Kiran Joshi',
                'contact_number': '9876543214',
                'age_group': '18-25',
                'sabha_type': 'yuvak',
                'address': '654 Bhakti Street',
                'join_date': '2023-04-01',
                'photo_url': 'https://via.placeholder.com/150',
                'created_at': datetime.now().isoformat()
            }
        ]

        for devotee_data in devotees_data:
            existing = devotees_db.find_one({'contact_number': devotee_data['contact_number']})
            if not existing:
                result = devotees_db.insert_one(devotee_data)
                if result:
                    devotee_id = devotees_db.find_one({'_id': result.inserted_id}).get('devotee_id')
                    self.stdout.write(f'Created devotee: {devotee_data["name"]} (ID: {devotee_id})')

        # Create sample sabhas
        today = datetime.now().date()
        sabhas_data = [
            {
                'date': (today - timedelta(days=7)).isoformat(),
                'sabha_type': 'bal',
                'location': 'Main Hall',
                'start_time': '10:00',
                'end_time': '11:30',
                'created_at': datetime.now().isoformat()
            },
            {
                'date': (today - timedelta(days=6)).isoformat(),
                'sabha_type': 'yuvak',
                'location': 'Youth Center',
                'start_time': '18:00',
                'end_time': '19:30',
                'created_at': datetime.now().isoformat()
            },
            {
                'date': (today - timedelta(days=5)).isoformat(),
                'sabha_type': 'mahila',
                'location': 'Community Hall',
                'start_time': '16:00',
                'end_time': '17:30',
                'created_at': datetime.now().isoformat()
            },
            {
                'date': today.isoformat(),
                'sabha_type': 'sanyukt',
                'location': 'Main Temple',
                'start_time': '19:00',
                'end_time': '20:30',
                'created_at': datetime.now().isoformat()
            }
        ]

        for sabha_data in sabhas_data:
            existing = sabhas_db.find_one({
                'date': sabha_data['date'],
                'sabha_type': sabha_data['sabha_type']
            })
            if not existing:
                sabhas_db.insert_one(sabha_data)
                self.stdout.write(f'Created sabha: {sabha_data["sabha_type"]} on {sabha_data["date"]}')

        self.stdout.write(self.style.SUCCESS('Successfully seeded MongoDB with sample data!'))
        self.stdout.write('Login with: username=admin, password=admin123')