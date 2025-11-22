from attendance.mongodb_utils import get_mongodb
from bson import ObjectId
from datetime import datetime
import bcrypt

class AdminUser:
    def __init__(self, username, email, password=None, allowed_sabha_types=None, is_admin=False, can_delete=False, _id=None):
        self._id = _id or ObjectId()
        self.username = username
        self.email = email
        self.password_hash = self._hash_password(password) if password else None
        self.allowed_sabha_types = allowed_sabha_types or []
        self.is_admin = is_admin
        self.can_delete = can_delete
        self.created_at = datetime.now()
        self.is_active = True
    
    def _hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    @property
    def id(self):
        return str(self._id)
    
    def to_dict(self):
        return {
            '_id': self._id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'allowed_sabha_types': self.allowed_sabha_types,
            'is_admin': self.is_admin,
            'can_delete': self.can_delete,
            'created_at': self.created_at,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data):
        user = cls.__new__(cls)
        user._id = data.get('_id')
        user.username = data.get('username')
        user.email = data.get('email')
        user.password_hash = data.get('password_hash')
        user.allowed_sabha_types = data.get('allowed_sabha_types', [])
        user.is_admin = data.get('is_admin', False)
        user.can_delete = data.get('can_delete', False)
        user.created_at = data.get('created_at')
        user.is_active = data.get('is_active', True)
        return user

class AdminUserManager:
    def __init__(self):
        self.db = get_mongodb()
        self.collection = self.db.admin_users if self.db is not None else None
    
    def create_user(self, username, email, password, allowed_sabha_types=None, is_admin=False, can_delete=False):
        if self.collection is None:
            raise ValueError('MongoDB connection not available')
        if self.collection.find_one({'username': username}):
            raise ValueError('Username already exists')
        
        user = AdminUser(username, email, password, allowed_sabha_types, is_admin, can_delete)
        result = self.collection.insert_one(user.to_dict())
        user._id = result.inserted_id
        return user
    
    def get_user_by_username(self, username):
        if self.collection is None:
            return None
        data = self.collection.find_one({'username': username, 'is_active': True})
        return AdminUser.from_dict(data) if data else None
    
    def get_user_by_id(self, user_id):
        if self.collection is None:
            return None
        data = self.collection.find_one({'_id': ObjectId(user_id), 'is_active': True})
        return AdminUser.from_dict(data) if data else None
    
    def get_all_users(self):
        if self.collection is None:
            return []
        users = []
        for data in self.collection.find({'is_active': True}):
            users.append(AdminUser.from_dict(data))
        return users
    
    def update_user(self, user_id, **kwargs):
        if self.collection is None:
            return
        update_data = {}
        if 'allowed_sabha_types' in kwargs:
            update_data['allowed_sabha_types'] = kwargs['allowed_sabha_types']
        if 'is_admin' in kwargs:
            update_data['is_admin'] = kwargs['is_admin']
        if 'can_delete' in kwargs:
            update_data['can_delete'] = kwargs['can_delete']
        if 'email' in kwargs:
            update_data['email'] = kwargs['email']
        if 'password' in kwargs:
            update_data['password_hash'] = bcrypt.hashpw(kwargs['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        if update_data:
            self.collection.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})
    
    def delete_user(self, user_id):
        if self.collection is not None:
            self.collection.delete_one({'_id': ObjectId(user_id)})
    
    def authenticate(self, username, password):
        user = self.get_user_by_username(username)
        if user and user.check_password(password):
            return user
        return None