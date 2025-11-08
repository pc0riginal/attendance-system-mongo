# 🏛️ Temple Weekly Attendance System

A modern Django-based web application designed to help temple administrators efficiently record and track devotees' weekly sabha (assembly) attendance with a beautiful, responsive interface.

## ✨ Features

- **👥 User Management**: Admin and devotee roles with secure authentication
- **📋 Devotee Management**: Add, edit, and manage devotee information with photo support
- **📅 Sabha Management**: Create weekly sabha events (Bal, Yuvak, Mahila, Sanyukt)
- **✅ Attendance Tracking**: Mark attendance with status (Present, Absent, Late)
- **📊 Reports & Analytics**: View attendance reports with filtering and Excel export
- **📈 Dashboard**: Modern dashboard with statistics and quick actions
- **📱 Responsive Design**: Mobile-first Bootstrap 5 interface with modern gradient design
- **📤 Bulk Import**: Excel file upload for bulk devotee management
- **🎨 Modern UI**: Stripe-inspired design with smooth animations

## Installation & Setup

### Prerequisites
- Python 3.12+
- pip (Python package installer)

### Installation Steps

1. **Clone or download the project**
   ```bash
   cd d:\attendance
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create sample data (optional)**
   ```bash
   python manage.py seed_data
   ```
   This creates:
   - Admin user (username: `admin`, password: `admin123`)
   - Sample devotees and sabhas
   - Sample attendance records

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open your browser and go to: `http://127.0.0.1:8000`
   - Login with admin credentials: `admin` / `admin123`

## Usage

### Admin Functions
- **Dashboard**: View attendance statistics and quick actions
- **Devotees**: Add, edit, and manage devotee information
- **Sabhas**: Create weekly sabha events
- **Mark Attendance**: Record attendance for each sabha
- **Reports**: View and export attendance data

### Devotee Functions
- **View Attendance History**: See personal attendance records
- **Sabha Schedule**: View upcoming sabha events

## Project Structure

```
temple_attendance/
├── manage.py
├── requirements.txt
├── README.md
├── temple_attendance/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── attendance/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── management/
│       └── commands/
│           └── seed_data.py
├── templates/
│   ├── base.html
│   ├── registration/
│   │   └── login.html
│   └── attendance/
│       ├── dashboard.html
│       ├── devotee_list.html
│       ├── devotee_form.html
│       ├── sabha_list.html
│       ├── sabha_form.html
│       ├── mark_attendance.html
│       └── attendance_report.html
└── static/
    └── css/
```

## Data Models

### Devotee
- Name, contact number, age group
- Sabha type (Bal, Yuvak, Mahila, General)
- Address, join date
- Optional user account link

### Sabha
- Date, sabha type, location
- Start time, end time

### Attendance
- Devotee (Foreign Key)
- Sabha (Foreign Key)
- Status (Present, Absent, Late)
- Optional notes

## Technical Stack

- **Backend**: Django 5+, Python 3.12+
- **Frontend**: Bootstrap 5, HTML templates
- **Database**: SQLite (default)
- **Authentication**: Django's built-in auth system

## Customization

### Adding New Sabha Types
Edit the `SABHA_CHOICES` in `attendance/models.py`:
```python
SABHA_CHOICES = [
    ('bal', 'Bal Sabha'),
    ('yuvak', 'Yuvak Sabha'),
    ('mahila', 'Mahila Sabha'),
    ('general', 'General Sabha'),
    ('senior', 'Senior Sabha'),  # Add new types here
]
```

### Changing Theme Colors
Modify CSS variables in `templates/base.html`:
```css
:root {
    --temple-orange: #ff6b35;
    --temple-gold: #f7931e;
    --temple-red: #dc3545;
    --temple-dark: #2c3e50;
}
```

## Production Deployment

1. Set `DEBUG = False` in settings.py
2. Configure proper database (PostgreSQL/MySQL)
3. Set up static file serving
4. Configure email settings for notifications
5. Use environment variables for sensitive settings

## 🚀 Production Deployment

### Quick Deploy Script
```bash
python deploy.py
```

### Manual Production Setup

1. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your production values
   ```

2. **Install Production Dependencies**
   ```bash
   pip install -r requirements-prod.txt
   ```

3. **Database Setup**
   ```bash
   export DJANGO_SETTINGS_MODULE=temple_attendance.production_settings
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Static Files**
   ```bash
   python manage.py collectstatic
   ```

5. **Run Production Server**
   ```bash
   gunicorn temple_attendance.wsgi:application
   ```

### ☁️ Cloud Deployment

#### Heroku
```bash
heroku create your-temple-app
heroku config:set DJANGO_SETTINGS_MODULE=temple_attendance.production_settings
heroku config:set SECRET_KEY=your-secret-key
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

#### Railway/Render
- Set environment variables from `.env.example`
- Set build command: `pip install -r requirements-prod.txt`
- Set start command: `gunicorn temple_attendance.wsgi`

## 🔒 Security Features

- CSRF protection
- XSS filtering
- Secure headers
- SSL redirect (production)
- Session security
- Password validation

## 📊 Performance

- WhiteNoise for static files
- Compressed static files
- Optimized database queries
- Responsive caching

## 🐛 Support

For issues or questions:
- Create an issue in the GitHub repository
- Check the Django documentation
- Review the deployment logs