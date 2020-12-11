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

CREATE_LOAN_URL = reverse('lms:create_loan')


class CreateLoanTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.customer_login_token , self.agent_login_token, self.admin_login_token = setUp_users()

        all_admins = User.objects.filter(role='admin')
        self.admin_1 = all_admins.first()
        self.admin_2 = all_admins.last()

        all_agents = User.objects.filter(role='agent')
        self.agent_1 = all_agents.first()
        self.agent_2 = all_agents.last()

        all_customers = User.objects.filter(role='customer')
        self.customer_1 = all_customers.first()
        self.customer_2 = all_customers.last()       

        self.customer_loan_request = {
            'customer-id' : self.customer_1.id,
            'principal-amount' : "10000",
            'interest-rate' : "1",
            'tenure-months' : "12"
        } 
    
    def test_create_loan_by_customer(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.customer_login_token)
        res = self.client.post(CREATE_LOAN_URL, self.customer_loan_request)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_loan_by_agent_and_validate(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.post(CREATE_LOAN_URL, self.customer_loan_request)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)  

        last_loan = Loan.objects.last()

        self.assertEqual(last_loan.created_for.id, int(self.customer_loan_request['customer-id']))
        self.assertEqual(last_loan.created_by.id, self.agent_1.id)
        self.assertEqual(last_loan.principal_amount, int(self.customer_loan_request['principal-amount']))
        self.assertEqual(last_loan.tenure_months, int(self.customer_loan_request['tenure-months']))
        self.assertEqual(last_loan.interest_rate, float(self.customer_loan_request['interest-rate']))
        self.assertEqual(last_loan.emi, 888.49)

    def test_create_loan_for_agent(self):
        agent_loan_request = {
            'customer-id' : self.agent_1.id,
            'principal-amount' : 10000,
            'interest-rate' : 1,
            'tenure-months' : 12
        } 
                
        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.post(CREATE_LOAN_URL, agent_loan_request)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST) 
    
    def test_create_loan_for_admin(self):
        admin_loan_request = {
            'customer-id' : self.admin_1.id,
            'principal-amount' : 10000,
            'interest-rate' : 1,
            'tenure-months' : 12
        } 
                
        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.post(CREATE_LOAN_URL, admin_loan_request)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST) 


    def test_create_loan_by_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.admin_login_token)
        res = self.client.post(CREATE_LOAN_URL, self.customer_loan_request)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)        

    def test_invalid_loan_creation(self):
        invalid_loan_request = {
            'customer-id': self.customer_1.id,
            'interest-rate': 150,
            'principal-amount' : "one lakh rupees",
            'tenure-months' : "tweleve"
        }
        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.post(CREATE_LOAN_URL, invalid_loan_request)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  



    def test_inactive_customer_create_loan(self):
        inactive_customer = User.objects.last()
        inactive_customer.is_active = False
        inactive_customer.save()

        inactive_customer_loan_request = {
            'customer-id' : inactive_customer.id,
            'principal-amount' : 10000,
            'interest-rate' : 1,
            'tenure-months' : 12
        }
        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.post(CREATE_LOAN_URL, inactive_customer_loan_request)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  


    def test_create_loan_non_existent_user(self):
        payload = {
            'customer-id' : 999,
            'principal-amount' : 10000,
            'interest-rate' : 12,
            'tenure-months' : 12
        }

        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.post(CREATE_LOAN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)     

    def test_invalid_loan_value(self):
        payload = {
            'customer-id' : self.customer_1.id,
            'principal-amount' : -1000,
            'interest-rate' : 5000,
            'tenure-months' : 4.8
        }
        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.post(CREATE_LOAN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  
