from django.db import models
from django.contrib.auth.models import User
from .mongodb_utils import MongoDBManager
from bson import ObjectId
from datetime import datetime

class DevoteeManager:
    def __init__(self):
        self.mongodb_manager = MongoDBManager('devotees')
    
    def all(self):
        docs = self.mongodb_manager.find()
        return [Devotee.from_dict(doc) for doc in docs]
    
    def filter(self, **kwargs):
        query = {}
        if 'sabha_type__in' in kwargs:
            query['sabha_type'] = {'$in': kwargs['sabha_type__in']}
        elif 'sabha_type' in kwargs:
            query['sabha_type'] = kwargs['sabha_type']
        if 'name__icontains' in kwargs:
            query['name'] = {'$regex': kwargs['name__icontains'], '$options': 'i'}
        if 'contact_number__icontains' in kwargs:
            query['contact_number'] = {'$regex': kwargs['contact_number__icontains'], '$options': 'i'}
        
        docs = self.mongodb_manager.find(query)
        return [Devotee.from_dict(doc) for doc in docs]
    
    def get(self, **kwargs):
        query = {}
        if 'pk' in kwargs:
            query['_id'] = ObjectId(kwargs['pk'])
        docs = self.mongodb_manager.find(query)
        if docs:
            return Devotee.from_dict(docs[0])
        raise Devotee.DoesNotExist()
    
    def count(self):
        return self.mongodb_manager.count()

class Devotee:
    SABHA_CHOICES = [
        ('bal', 'Bal Sabha'),
        ('yuvak', 'Yuvak Sabha'),
        ('mahila', 'Mahila Sabha'),
        ('sanyukt', 'Sanyukt Sabha'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    
    DEVOTEE_TYPE_CHOICES = [
        ('haribhakt', 'Haribhakt'),
        ('gunbhavi', 'Gunbhavi'),
        ('karyakar', 'Karyakar'),
    ]
    
    class DoesNotExist(Exception):
        pass
    
    objects = DevoteeManager()
    
    def __init__(self, devotee_id=None, devotee_type='haribhakt', name=None, contact_number=None, 
                 date_of_birth=None, gender=None, age=None, sabha_type=None, address_line='', 
                 landmark='', zone='', join_date=None, photo_url=None, _id=None):
        self._id = _id or ObjectId()
        self.devotee_id = devotee_id
        self.devotee_type = devotee_type
        self.name = name
        self.contact_number = contact_number
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.age = age
        self.sabha_type = sabha_type
        self.address_line = address_line
        self.landmark = landmark
        self.zone = zone
        self.join_date = join_date
        self.photo_url = photo_url
    
    @property
    def pk(self):
        return str(self._id)
    
    @property
    def id(self):
        return str(self._id)
    
    def get_sabha_type_display(self):
        for choice in self.SABHA_CHOICES:
            if choice[0] == self.sabha_type:
                return choice[1]
        return self.sabha_type
    
    def save(self):
        mongodb_manager = MongoDBManager('devotees')
        doc = {
            'devotee_id': self.devotee_id,
            'devotee_type': self.devotee_type,
            'name': self.name,
            'contact_number': self.contact_number,
            'date_of_birth': self.date_of_birth,
            'gender': self.gender,
            'age': self.age,
            'sabha_type': self.sabha_type,
            'address_line': self.address_line,
            'landmark': self.landmark,
            'zone': self.zone,
            'join_date': self.join_date,
            'photo_url': self.photo_url
        }
        if hasattr(self, '_id') and self._id:
            mongodb_manager.update_one({'_id': self._id}, doc)
        else:
            result = mongodb_manager.insert_one(doc)
            if result:
                self._id = result.inserted_id
    
    @classmethod
    def from_dict(cls, doc):
        return cls(
            _id=doc.get('_id'),
            devotee_id=doc.get('devotee_id'),
            devotee_type=doc.get('devotee_type', 'haribhakt'),
            name=doc.get('name'),
            contact_number=doc.get('contact_number'),
            date_of_birth=doc.get('date_of_birth'),
            gender=doc.get('gender'),
            age=doc.get('age'),
            sabha_type=doc.get('sabha_type'),
            address_line=doc.get('address_line', ''),
            landmark=doc.get('landmark', ''),
            zone=doc.get('zone', ''),
            join_date=doc.get('join_date'),
            photo_url=doc.get('photo_url')
        )
    
    def __str__(self):
        return f"{self.name} - {self.get_sabha_type_display()}"

class SabhaManager:
    def __init__(self):
        self.mongodb_manager = MongoDBManager('sabhas')
    
    def all(self):
        docs = self.mongodb_manager.find(sort=[('date', -1)])
        return [Sabha.from_dict(doc) for doc in docs]
    
    def filter(self, **kwargs):
        query = {}
        if 'sabha_type__in' in kwargs:
            query['sabha_type'] = {'$in': kwargs['sabha_type__in']}
        elif 'sabha_type' in kwargs:
            query['sabha_type'] = kwargs['sabha_type']
        
        docs = self.mongodb_manager.find(query, sort=[('date', -1)])
        return [Sabha.from_dict(doc) for doc in docs]
    
    def get(self, **kwargs):
        query = {}
        if 'pk' in kwargs:
            query['_id'] = ObjectId(kwargs['pk'])
        docs = self.mongodb_manager.find(query)
        if docs:
            return Sabha.from_dict(docs[0])
        raise Sabha.DoesNotExist()

class Sabha:
    SABHA_CHOICES = [
        ('bal', 'Bal Sabha'),
        ('yuvak', 'Yuvak Sabha'),
        ('mahila', 'Mahila Sabha'),
        ('sanyukt', 'Sanyukt Sabha'),
    ]
    
    class DoesNotExist(Exception):
        pass
    
    objects = SabhaManager()
    
    def __init__(self, date=None, sabha_type=None, location=None, start_time=None, end_time=None, mandal=None, xetra=None, _id=None):
        self._id = _id or ObjectId()
        self.date = date
        self.sabha_type = sabha_type
        self.location = location
        self.start_time = start_time
        self.end_time = end_time
        self.mandal = mandal
        self.xetra = xetra
    
    @property
    def pk(self):
        return str(self._id)
    
    @property
    def id(self):
        return str(self._id)
    
    def get_sabha_type_display(self):
        for choice in self.SABHA_CHOICES:
            if choice[0] == self.sabha_type:
                return choice[1]
        return self.sabha_type
    
    def save(self):
        mongodb_manager = MongoDBManager('sabhas')
        doc = {
            'date': self.date,
            'sabha_type': self.sabha_type,
            'location': self.location,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'mandal': self.mandal,
            'xetra': self.xetra
        }
        if hasattr(self, '_id') and self._id:
            mongodb_manager.update_one({'_id': self._id}, doc)
        else:
            result = mongodb_manager.insert_one(doc)
            if result:
                self._id = result.inserted_id
    
    @classmethod
    def from_dict(cls, doc):
        return cls(
            _id=doc.get('_id'),
            date=doc.get('date'),
            sabha_type=doc.get('sabha_type'),
            location=doc.get('location'),
            start_time=doc.get('start_time'),
            end_time=doc.get('end_time'),
            mandal=doc.get('mandal'),
            xetra=doc.get('xetra')
        )
    
    def __str__(self):
        return f"{self.get_sabha_type_display()} - {self.date}"

class AttendanceManager:
    def __init__(self):
        self.mongodb_manager = MongoDBManager('attendance_records')
    
    def all(self):
        docs = self.mongodb_manager.find()
        return [Attendance.from_dict(doc) for doc in docs]
    
    def filter(self, **kwargs):
        query = {}
        if 'sabha' in kwargs:
            query['sabha_id'] = str(kwargs['sabha'].pk)
        if 'sabha__date__range' in kwargs:
            # Handle date range filtering
            pass
        if 'status' in kwargs:
            query['status'] = kwargs['status']
        
        docs = self.mongodb_manager.find(query)
        return [Attendance.from_dict(doc) for doc in docs]
    
    def get_or_create(self, **kwargs):
        defaults = kwargs.pop('defaults', {})
        query = {}
        if 'devotee' in kwargs:
            query['devotee_id'] = str(kwargs['devotee'].pk)
        if 'sabha' in kwargs:
            query['sabha_id'] = str(kwargs['sabha'].pk)
        
        doc = self.mongodb_manager.find_one(query)
        if doc:
            return Attendance.from_dict(doc), False
        else:
            new_doc = {**query, **defaults, 'timestamp': datetime.now()}
            result = self.mongodb_manager.insert_one(new_doc)
            if result:
                new_doc['_id'] = result.inserted_id
                return Attendance.from_dict(new_doc), True
        return None, False

class Attendance:
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ]
    
    objects = AttendanceManager()
    
    def __init__(self, devotee_id=None, sabha_id=None, status='absent', notes='', timestamp=None, _id=None):
        self._id = _id or ObjectId()
        self.devotee_id = devotee_id
        self.sabha_id = sabha_id
        self.status = status
        self.notes = notes
        self.timestamp = timestamp or datetime.now()
    
    @property
    def pk(self):
        return str(self._id)
    
    @property
    def id(self):
        return str(self._id)
    
    @property
    def devotee(self):
        # Return devotee object by ID
        return Devotee.objects.get(pk=self.devotee_id)
    
    @property
    def sabha(self):
        # Return sabha object by ID
        return Sabha.objects.get(pk=self.sabha_id)
    
    def get_status_display(self):
        for choice in self.STATUS_CHOICES:
            if choice[0] == self.status:
                return choice[1]
        return self.status
    
    def save(self):
        mongodb_manager = MongoDBManager('attendance_records')
        doc = {
            'devotee_id': self.devotee_id,
            'sabha_id': self.sabha_id,
            'status': self.status,
            'notes': self.notes,
            'timestamp': self.timestamp
        }
        if hasattr(self, '_id') and self._id:
            mongodb_manager.update_one({'_id': self._id}, doc)
        else:
            result = mongodb_manager.insert_one(doc)
            if result:
                self._id = result.inserted_id
    
    @classmethod
    def from_dict(cls, doc):
        return cls(
            _id=doc.get('_id'),
            devotee_id=doc.get('devotee_id'),
            sabha_id=doc.get('sabha_id'),
            status=doc.get('status', 'absent'),
            notes=doc.get('notes', ''),
            timestamp=doc.get('timestamp')
        )
    
    def __str__(self):
        return f"{self.devotee_id} - {self.sabha_id} - {self.get_status_display()}"

# UserProfile removed - all user data stored in MongoDB via admin_panel