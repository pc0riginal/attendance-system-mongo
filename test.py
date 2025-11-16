import pandas as pd
import random
from faker import Faker
from datetime import datetime, date

# Initialize Faker
fake = Faker("en_IN")

# Define categories
sabha_types = ["bal", "yuvak", "mahila", "sanyukt"]
devotee_types = ["haribhakt", "gunbhavi", "karyakar"]
genders = ["male", "female"]

# Define prefixes for devotee_id
prefix_map = {
    "bal": "b",
    "yuvak": "y", 
    "mahila": "m",
    "sanyukt": "s"
}

# Counter for each sabha type
counters = {"b": 1, "y": 1, "m": 1, "s": 1}

records = []

def generate_phone():
    """Generate a valid 10-digit Indian phone number."""
    start_digit = random.choice(["6", "7", "8", "9"])
    remaining = "".join([str(random.randint(0, 9)) for _ in range(9)])
    return start_digit + remaining

def calculate_age(birth_date):
    """Calculate age from birth date."""
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

# Generate 500 random devotee records
for i in range(1, 501):
    name = fake.name()
    contact_number = generate_phone()
    sabha_type = random.choice(sabha_types)
    devotee_type = random.choice(devotee_types)
    gender = random.choice(genders)
    date_of_birth = fake.date_between(start_date="-70y", end_date="-5y")
    age = calculate_age(date_of_birth)
    address_line = fake.street_address()
    landmark = f"Near {fake.company()}"
    zone = f"Zone {random.choice(['A', 'B', 'C', 'D'])}"
    join_date = fake.date_between(start_date="-2y", end_date="today")
    
    # Generate devotee_id with prefix
    prefix = prefix_map[sabha_type]
    devotee_id = f"{prefix}{counters[prefix]}"
    counters[prefix] += 1
    
    records.append({
        "devotee_id": devotee_id,
        "name": name,
        "contact_number": contact_number,
        "sabha_type": sabha_type,
        "devotee_type": devotee_type,
        "date_of_birth": date_of_birth.strftime("%Y-%m-%d"),
        "gender": gender,
        "age": age,
        "address_line": address_line,
        "landmark": landmark,
        "zone": zone,
        "join_date": join_date.strftime("%Y-%m-%d")
    })

# Create DataFrame
df = pd.DataFrame(records)

# Save to Excel
df.to_excel("devotee_data.xlsx", index=False)

print("✅ Excel file 'devotee_data.xlsx' created successfully with 500 records and new devotee structure.")
