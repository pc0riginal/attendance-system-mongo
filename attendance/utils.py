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
        required_columns = ['name', 'contact_number', 'sabha_type', 'photo_url']
        optional_columns = ['age_group', 'address', 'join_date']
        
        # Check if required columns exist
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return None, f"Missing required columns: {', '.join(missing_columns)}"
        
        errors = []
        valid_rows = []
        
        for index, row in df.iterrows():
            row_errors = []
            
            # Validate name
            if not row['name'] or pd.isna(row['name']) or str(row['name']).strip() == '':
                row_errors.append("Name is required")
            
            # Validate phone
            phone_valid, phone_error = validate_phone(row['contact_number'])
            if not phone_valid:
                row_errors.append(phone_error)
            
            # Validate sabha type
            sabha_valid, sabha_error = validate_sabha_type(row['sabha_type'])
            if not sabha_valid:
                row_errors.append(sabha_error)
            
            # Validate photo URL
            url_valid, url_error = validate_url(row['photo_url'])
            if not url_valid:
                row_errors.append(url_error)
            
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
                # Prepare valid row data
                valid_row = {
                    'name': str(row['name']).strip(),
                    'contact_number': str(row['contact_number']).strip(),
                    'sabha_type': str(row['sabha_type']).lower().strip(),
                    'photo_url': str(row['photo_url']).strip(),
                    'age_group': str(row.get('age_group', '')).strip() if not pd.isna(row.get('age_group')) else '',
                    'address': str(row.get('address', '')).strip() if not pd.isna(row.get('address')) else '',
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