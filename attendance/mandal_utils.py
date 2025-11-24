from .mongodb_utils import MongoDBManager

def get_mandal_choices():
    """Get mandal choices from database for dropdowns"""
    mandals_db = MongoDBManager('mandals')
    mandals = list(mandals_db.find(sort=[('display_name', 1)]))
    return [(mandal['name'], mandal['display_name']) for mandal in mandals]

def get_mandal_names():
    """Get list of mandal names for validation"""
    mandals_db = MongoDBManager('mandals')
    mandals = list(mandals_db.find({}, {'name': 1}))
    return [mandal['name'] for mandal in mandals]