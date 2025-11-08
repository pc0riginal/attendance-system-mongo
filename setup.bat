@echo off
echo Setting up Temple Attendance System...

echo Installing dependencies...
pip install -r requirements.txt

echo Running migrations...
python manage.py makemigrations
python manage.py migrate

echo Creating sample data...
python manage.py seed_data

echo Setup complete!
echo.
echo To start the server, run: python manage.py runserver
echo Then visit: http://127.0.0.1:8000
echo Login with: admin / admin123
pause