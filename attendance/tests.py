from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, time
from .models import Devotee, Sabha, Attendance

class DevoteeModelTest(TestCase):
    def test_devotee_creation(self):
        devotee = Devotee.objects.create(
            name="Test Devotee",
            contact_number="1234567890",
            age_group="20-30",
            sabha_type="yuvak",
            address="Test Address",
            join_date=date.today()
        )
        self.assertEqual(str(devotee), "Test Devotee - Yuvak Sabha")

class SabhaModelTest(TestCase):
    def test_sabha_creation(self):
        sabha = Sabha.objects.create(
            date=date.today(),
            sabha_type="bal",
            location="Test Hall",
            start_time=time(10, 0),
            end_time=time(11, 30)
        )
        self.assertEqual(sabha.sabha_type, "bal")

class AttendanceModelTest(TestCase):
    def setUp(self):
        self.devotee = Devotee.objects.create(
            name="Test Devotee",
            contact_number="1234567890",
            age_group="20-30",
            sabha_type="yuvak",
            address="Test Address",
            join_date=date.today()
        )
        self.sabha = Sabha.objects.create(
            date=date.today(),
            sabha_type="yuvak",
            location="Test Hall",
            start_time=time(10, 0),
            end_time=time(11, 30)
        )

    def test_attendance_creation(self):
        attendance = Attendance.objects.create(
            devotee=self.devotee,
            sabha=self.sabha,
            status="present"
        )
        self.assertEqual(attendance.status, "present")