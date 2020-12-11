from django.test import TestCase
from lms.models import User, Loan
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import re
from lms.utils import dprint
import time
from pprint import pprint
from .helper_setUp_func import setUp_users

class ApproveLoanTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.customer_login_token , self.agent_login_token, self.admin_login_token = setUp_users()

        all_admins = User.objects.filter(role='admin')
        self.admin_1 = all_admins.first()
        self.admin_2 = all_admins.last()

        all_agents = User.objects.filter(role='agent')
        self.agent_1 = all_agents.first()

        all_customers = User.objects.filter(role='customer')
        self.customer_1 = all_customers.first()

        #create loan
        customer_loan_request = {
            'customer-id' : self.customer_1.id,
            'principal-amount' : "10000",
            'interest-rate' : "1",
            'tenure-months' : "12"
        }
        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        self.client.post(reverse('lms:create_loan'), customer_loan_request)        

    def test_approve_loan_by_customer(self):
        loan_obj = Loan.objects.last()
        approve_loan_url = reverse('lms:approve_loan' , kwargs={'id' : loan_obj.id})
        self.client.credentials(HTTP_AUTHORIZATION=self.customer_login_token)
        res = self.client.post(approve_loan_url)

        self.assertFalse(loan_obj.is_approved)
        self.assertFalse(loan_obj.status=='approved')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_approve_loan_by_agent(self):
        loan_obj = Loan.objects.last()
        approve_loan_url = reverse('lms:approve_loan' , kwargs={'id' : loan_obj.id})
        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.post(approve_loan_url)

        self.assertFalse(loan_obj.is_approved)
        self.assertFalse(loan_obj.status=='approved')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_approve_loan_by_admin(self):
        loan_obj = Loan.objects.last()
        self.assertFalse(loan_obj.is_approved)
        approve_loan_url = reverse('lms:approve_loan' , kwargs={'id' : loan_obj.id})
        self.client.credentials(HTTP_AUTHORIZATION=self.admin_login_token)
        res = self.client.post(approve_loan_url)

        loan_obj = Loan.objects.last()
        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(loan_obj.is_approved)
        self.assertEqual(loan_obj.status,'approved')

    def test_aprove_non_existent_loan(self):
        approve_loan_url = reverse('lms:approve_loan' , kwargs={'id' : 879})
        self.client.credentials(HTTP_AUTHORIZATION=self.admin_login_token)
        res = self.client.post(approve_loan_url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
