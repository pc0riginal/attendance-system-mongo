from django.core.management.base import BaseCommand
from attendance.mongodb_utils import MongoDBManager

class Command(BaseCommand):
    help = 'Fix MongoDB indexes - remove unique constraint on contact_number'

    def handle(self, *args, **options):
        devotees_db = MongoDBManager('devotees')
        
        if devotees_db._ensure_connection():
            try:
                # Drop existing unique index on contact_number
                devotees_db.collection.drop_index([('contact_number', 1)])
                self.stdout.write('Dropped unique index on contact_number')
            except Exception as e:
                self.stdout.write(f'Index drop failed (may not exist): {e}')
            
            try:
                # Create unique index on devotee_id
                devotees_db.collection.create_index([('devotee_id', 1)], unique=True)
                self.stdout.write('Created unique index on devotee_id')
            except Exception as e:
                self.stdout.write(f'Index creation failed: {e}')
            
            self.stdout.write(self.style.SUCCESS('Index fix completed'))
        else:
            self.stdout.write(self.style.ERROR('Database connection failed'))