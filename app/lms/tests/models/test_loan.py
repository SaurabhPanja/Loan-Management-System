from django.test import TestCase
from lms.models import User, Loan
from app.settings import SECRET_KEY
import hashlib

class LoanModelTest(TestCase):
    def setUp(self):
        User().create_user(email="test@gmail.com", password="password", role='customer')
        User().create_user(email="agent@gmai.com", password="password", role='agent')
        self.customer = User.objects.filter(role='customer').first()
        self.agent = User.objects.filter(role='agent').first()

    def test_invalid_value(self):
        error_raised = False
        try:
            Loan.objects.create(
                created_for=self.customer,
                created_by=self.agent,
                principal_amount=-1000,
                interest_rate=5000,
                tenure_months = 1.5,
                emi = 77
            )
        except:
            error_raised = True

        self.assertTrue(error_raised)

