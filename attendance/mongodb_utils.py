from django.conf import settings
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

_mongo_client = None
_mongodb = None

def get_mongodb():
    """Get MongoDB database instance"""
    global _mongo_client, _mongodb
    
    if _mongodb is None:
        try:
            print(f"Connecting to MongoDB: {settings.MONGODB_NAME}")
            # Add connection timeout and retry settings
            _mongo_client = MongoClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=30000,
                socketTimeoutMS=60000,
                connectTimeoutMS=30000,
                maxPoolSize=50,
                retryWrites=True,
                ssl=True,
                tlsAllowInvalidCertificates=False
            )
            _mongodb = _mongo_client[settings.MONGODB_NAME]
            # Test connection
            server_info = _mongo_client.server_info()
            print(f"MongoDB connected successfully. Server version: {server_info.get('version')}")
            
            # Test database access
            collections = _mongodb.list_collection_names()
            print(f"Available collections: {collections}")
            
        except Exception as e:
            print(f"MongoDB connection error: {e}")
            import traceback
            traceback.print_exc()
            _mongodb = None
    
    return _mongodb

class MongoDBManager:
    """Manager class for MongoDB operations"""
    
    def __init__(self, collection_name):
        self.collection_name = collection_name
        self.db = get_mongodb()
        self.collection = self.db[collection_name] if self.db is not None else None
        self._ensure_indexes(collection_name)
    
    def _ensure_connection(self):
        """Ensure MongoDB connection is healthy"""
        if self.db is None:
            self.db = get_mongodb()
            if self.db is not None and hasattr(self, 'collection_name'):
                self.collection = self.db[self.collection_name]
            else:
                self.collection = None
        return self.collection is not None
    
    def get_next_devotee_id(self, sabha_type=None):
        """Get next auto-increment devotee_id with prefix based on sabha_type"""
        if self.collection_name == 'devotees' and self._ensure_connection():
            # Define prefixes for each sabha type
            prefixes = {
                'bal': 'b',
                'yuvak': 'y', 
                'mahila': 'm',
                'sanyukt': 's'
            }
            
            prefix = prefixes.get(sabha_type, 'g')  # 'g' for general/unknown
            
            # Find the highest number for this prefix
            pattern = f'^{prefix}\\d+$'
            existing_ids = list(self.collection.find(
                {'devotee_id': {'$regex': pattern}},
                {'devotee_id': 1}
            ))
            
            max_num = 0
            for doc in existing_ids:
                devotee_id = doc.get('devotee_id', '')
                if devotee_id.startswith(prefix):
                    try:
                        num = int(devotee_id[len(prefix):])
                        max_num = max(max_num, num)
                    except ValueError:
                        continue
            
            return f'{prefix}{max_num + 1}'
        return 'g1'
    
    def insert_one(self, document):
        """Insert a single document"""
        if self._ensure_connection():
            try:
                # devotee_id is now mandatory and provided by user
                return self.collection.insert_one(document)
            except Exception as e:
                print(f"Error inserting document into {self.collection_name}: {e}")
                return None
        else:
            print(f"No connection available for {self.collection_name}")
            return None
    
    def insert_many(self, documents):
        """Insert multiple documents"""
        if self.collection is not None:
            return self.collection.insert_many(documents)
        return None
    
    def find_one(self, query):
        """Find a single document"""
        if self._ensure_connection():
            return self.collection.find_one(query)
        return None
    
    def find(self, query=None, sort=None, limit=None, skip=None):
        """Find multiple documents"""
        if self._ensure_connection():
            try:
                cursor = self.collection.find(query or {})
                if sort:
                    cursor = cursor.sort(sort)
                if skip:
                    cursor = cursor.skip(skip)
                if limit:
                    cursor = cursor.limit(limit)
                result = list(cursor)
                print(f"Found {len(result)} documents in {self.collection_name}")
                return result
            except Exception as e:
                print(f"Error finding documents in {self.collection_name}: {e}")
                return []
        print(f"No connection to {self.collection_name}")
        return []
    
    def update_one(self, query, update):
        """Update a single document with retry logic"""
        if self._ensure_connection():
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    return self.collection.update_one(query, {'$set': update})
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    print(f"Update attempt {attempt + 1} failed: {e}")
                    import time
                    time.sleep(1)  # Wait 1 second before retry
        return None
    
    def update_many(self, query, update):
        """Update multiple documents"""
        if self.collection is not None:
            return self.collection.update_many(query, {'$set': update})
        return None
    
    def delete_one(self, query):
        """Delete a single document"""
        if self.collection is not None:
            return self.collection.delete_one(query)
        return None
    
    def delete_many(self, query):
        """Delete multiple documents"""
        if self.collection is not None:
            return self.collection.delete_many(query)
        return None
    
    def count(self, query=None):
        """Count documents"""
        if self._ensure_connection():
            try:
                count = self.collection.count_documents(query or {})
                print(f"Count in {self.collection_name}: {count}")
                return count
            except Exception as e:
                print(f"Error counting documents in {self.collection_name}: {e}")
                return 0
        return 0
    
    def _ensure_indexes(self, collection_name):
        """Create indexes for better performance"""
        if self.collection is None:
            return
        
        try:
            if collection_name == 'attendance_records':
                self.collection.create_index([('sabha_id', 1), ('devotee_id', 1)], unique=True)
                self.collection.create_index([('sabha_id', 1)])
                self.collection.create_index([('devotee_id', 1)])
            elif collection_name == 'devotees':
                self.collection.create_index([('sabha_type', 1)])
                self.collection.create_index([('devotee_id', 1)], unique=True)
            elif collection_name == 'sabhas':
                self.collection.create_index([('date', -1)])
        except Exception:
            pass  # Indexes may already exist
