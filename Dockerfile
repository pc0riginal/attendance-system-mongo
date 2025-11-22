FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput --clear

ENV DEBUG=False

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "temple_attendance.wsgi:application"]