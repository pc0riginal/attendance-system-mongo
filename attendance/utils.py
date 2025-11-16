import pandas as pd
import re
from urllib.parse import urlparse
from .models import Devotee
from datetime import datetime

def validate_phone(phone):
    """Validate phone number"""
    if not phone or pd.isna(phone):
        return False, "Phone number is required"
    
    phone_str = str(phone).strip()
    if not phone_str.isdigit() or len(phone_str) < 10:
        return False, "Phone number must be at least 10 digits"
    
    return True, None

def validate_url(url):
    """Validate photo URL"""
    if not url or pd.isna(url):
        return False, "Photo URL is required"
    
    url_str = str(url).strip()
    try:
        result = urlparse(url_str)
        if not all([result.scheme, result.netloc]):
            return False, "Invalid URL format"
        
        if result.scheme not in ['http', 'https']:
            return False, "URL must start with http:// or https://"
        
        return True, None
    except:
        return False, "Invalid URL format"

def validate_sabha_type(sabha_type):
    """Validate sabha type"""
    if not sabha_type or pd.isna(sabha_type):
        return False, "Sabha type is required"
    
    sabha_str = str(sabha_type).lower().strip()
    valid_types = [choice[0] for choice in Devotee.SABHA_CHOICES]
    if sabha_str not in valid_types:
        return False, f"Invalid sabha type. Must be one of: {', '.join(valid_types)}"
    
    return True, None

def process_excel_file(file_path, sabha_type_filter=None):
    """Process Excel file and validate data"""
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Expected columns
        required_columns = ['devotee_id', 'name', 'contact_number', 'sabha_type', 'devotee_type', 'date_of_birth', 'gender']
        optional_columns = ['age', 'address_line', 'landmark', 'zone', 'join_date']
        
        # Check if required columns exist
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return None, f"Missing required columns: {', '.join(missing_columns)}"
        
        errors = []
        valid_rows = []
        
        for index, row in df.iterrows():
            row_errors = []
            
            # Validate devotee_id (mandatory string with prefix)
            if not row['devotee_id'] or pd.isna(row['devotee_id']):
                row_errors.append("Devotee ID is required")
            else:
                devotee_id_str = str(row['devotee_id']).strip()
                # Check format: prefix + number (e.g., p1, m2, y3, b4)
                if not re.match(r'^[a-zA-Z]\d+$', devotee_id_str):
                    row_errors.append("Devotee ID must be in format: prefix + number (e.g., p1, m2, y3, b4)")
            
            # Validate name (mandatory)
            if not row['name'] or pd.isna(row['name']) or str(row['name']).strip() == '':
                row_errors.append("Name is required")
            
            # Validate phone (mandatory)
            phone_valid, phone_error = validate_phone(row['contact_number'])
            if not phone_valid:
                row_errors.append(phone_error)
            
            # Validate sabha type (mandatory)
            sabha_valid, sabha_error = validate_sabha_type(row['sabha_type'])
            if not sabha_valid:
                row_errors.append(sabha_error)
            
            # Validate devotee_type (mandatory)
            if not row['devotee_type'] or pd.isna(row['devotee_type']):
                row_errors.append("Devotee type is required")
            else:
                devotee_type_str = str(row['devotee_type']).lower().strip()
                valid_types = [choice[0] for choice in Devotee.DEVOTEE_TYPE_CHOICES]
                if devotee_type_str not in valid_types:
                    row_errors.append(f"Invalid devotee type. Must be one of: {', '.join(valid_types)}")
            
            # Validate date_of_birth (mandatory)
            if not row['date_of_birth'] or pd.isna(row['date_of_birth']):
                row_errors.append("Date of birth is required")
            else:
                try:
                    if isinstance(row['date_of_birth'], str):
                        dob = datetime.strptime(row['date_of_birth'], '%Y-%m-%d').date()
                    else:
                        dob = row['date_of_birth'].date()
                    
                    if dob > datetime.now().date():
                        row_errors.append("Date of birth cannot be in the future")
                except:
                    row_errors.append("Invalid date of birth format. Use YYYY-MM-DD")
            
            # Validate gender (mandatory)
            if not row['gender'] or pd.isna(row['gender']):
                row_errors.append("Gender is required")
            else:
                gender_str = str(row['gender']).lower().strip()
                valid_genders = [choice[0] for choice in Devotee.GENDER_CHOICES]
                if gender_str not in valid_genders:
                    row_errors.append(f"Invalid gender. Must be one of: {', '.join(valid_genders)}")
            
            # Apply sabha type filter if specified
            if sabha_type_filter and str(row['sabha_type']).lower() != sabha_type_filter:
                continue
            
            if row_errors:
                errors.append({
                    'row': index + 2,  # +2 because Excel rows start at 1 and we have header
                    'errors': row_errors,
                    'data': row.to_dict()
                })
            else:
                # Calculate age from date_of_birth
                age = 0
                dob = None
                try:
                    if isinstance(row['date_of_birth'], str):
                        dob = datetime.strptime(row['date_of_birth'], '%Y-%m-%d').date()
                    else:
                        dob = row['date_of_birth'].date()
                    
                    today = datetime.now().date()
                    age = today.year - dob.year
                    if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
                        age -= 1
                except:
                    pass
                
                # Prepare valid row data
                valid_row = {
                    'devotee_id': str(row['devotee_id']).strip(),
                    'name': str(row['name']).strip(),
                    'contact_number': str(row['contact_number']).strip(),
                    'sabha_type': str(row['sabha_type']).lower().strip(),
                    'devotee_type': str(row['devotee_type']).lower().strip(),
                    'date_of_birth': dob,
                    'gender': str(row['gender']).lower().strip(),
                    'age': int(row.get('age', age)) if not pd.isna(row.get('age')) and str(row.get('age')).isdigit() else age,
                    'address_line': str(row.get('address_line', '')).strip() if not pd.isna(row.get('address_line')) else '',
                    'landmark': str(row.get('landmark', '')).strip() if not pd.isna(row.get('landmark')) else '',
                    'zone': str(row.get('zone', '')).strip() if not pd.isna(row.get('zone')) else '',
                    'photo_url': '',
                    'join_date': datetime.now().date()
                }
                
                # Handle join_date if provided
                if 'join_date' in row and not pd.isna(row['join_date']):
                    try:
                        if isinstance(row['join_date'], str):
                            valid_row['join_date'] = datetime.strptime(row['join_date'], '%Y-%m-%d').date()
                        else:
                            valid_row['join_date'] = row['join_date'].date()
                    except:
                        valid_row['join_date'] = datetime.now().date()
                
                valid_rows.append(valid_row)
        
        return {'valid_rows': valid_rows, 'errors': errors}, None
        
    except Exception as e:
        return None, f"Error processing file: {str(e)}"

def save_devotees(valid_rows):
    """Save valid devotee data to database"""
    created_count = 0
    updated_count = 0
    
    for row_data in valid_rows:
        devotee, created = Devotee.objects.update_or_create(
            contact_number=row_data['contact_number'],
            defaults=row_data
        )
        
        if created:
            created_count += 1
        else:
            updated_count += 1
    
    return created_count, updated_count