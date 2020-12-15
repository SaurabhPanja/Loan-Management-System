from django.test import TestCase
from lms.models import User, Loan, EditLoanHistory
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import re
from lms.utils import dprint
import time
from pprint import pprint
from .helper_setUp_func import setUp_users
from datetime import date

QUERY_LOAN_URL = reverse('lms:query_loan')

class ListandViewLoanTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.customer_login_token, self.agent_login_token, self.admin_login_token = setUp_users()

        all_admins = User.objects.filter(role='admin')
        self.admin = all_admins.first()

        all_agents = User.objects.filter(role='agent')
        self.agent = all_agents.first()
        
        all_customers = User.objects.filter(role='customer')
        self.customer_1 = all_customers.first()
        self.customer_2 = all_customers.last()

        customer_loan_request_1 = {
            'customer-id' : self.customer_1.id,
            'principal-amount' : "10000",
            'interest-rate' : "1",
            'tenure-months' : "12"
        } 
        customer_loan_request_2 = {
            'customer-id' : self.customer_2.id,
            'principal-amount' : "999",
            'interest-rate' : "1",
            'tenure-months' : "4"
        }
        customer_loan_request_3 = {
            'customer-id' : self.customer_1.id,
            'principal-amount' : "1000000",
            'interest-rate' : "5",
            'tenure-months' : "60"
        }

        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        self.client.post(reverse('lms:create_loan'),customer_loan_request_1)   
        self.client.post(reverse('lms:create_loan'),customer_loan_request_2) 
        self.client.post(reverse('lms:create_loan'),customer_loan_request_3)      

        loan_1 = Loan.objects.first()
        loan_2 = Loan.objects.last()

        approve_loan_url = reverse('lms:approve_loan' , kwargs={'id' : loan_1.id})
        self.client.credentials(HTTP_AUTHORIZATION=self.admin_login_token)
        self.client.post(approve_loan_url)     

        edit_loan_request = {
            'principal-amount' : 50000,
            'interest-rate' : 3,
            'tenure-months' : 11,
            'status' : 'rejected'
        }
        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        self.client.post(reverse('lms:edit_loan', kwargs={'id' : loan_2.id}), edit_loan_request)

    def test_list_all_loans_by_agent(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.get(QUERY_LOAN_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        response = res.json()
        loan_count = len(response['loans'])

        self.assertEqual(loan_count, 3)

    def test_list_all_loans_by_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.admin_login_token)
        res = self.client.get(QUERY_LOAN_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        response = res.json()
        loan_count = len(response['loans'])

        self.assertEqual(loan_count, 3)        

    def test_list_own_loans_by_customer(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.customer_login_token)
        res = self.client.get(QUERY_LOAN_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        response = res.json()
        loan_count = len(response['loans'])

        self.assertEqual(loan_count, 2)        

    def test_filter_by_created_date(self):
        created_date = date.today().strftime('%d/%m/%Y')
        query_payload = {
            'created-date' : created_date
        }
        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.get(QUERY_LOAN_URL, query_payload)
        response = res.json()

        loan_count = len(response['loans'])
        self.assertEqual(loan_count, 3) 

        failed = False

        for loan in response['loans']:
            failed = loan['created_at'] == created_date

        self.assertFalse(failed)  

    def test_filter_by_updated_date(self):
        updated_date = date.today().strftime('%d/%m/%Y')
        query_payload = {
            'updated-date' : updated_date
        }
        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.get(QUERY_LOAN_URL, query_payload)
        response = res.json()

        loan_count = len(response['loans'])
        self.assertEqual(loan_count, 3) 

        failed = False

        for loan in response['loans']:
            failed = loan['updated_at'] == updated_date

        self.assertFalse(failed)        

    def test_filter_by_loan_status(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.get(QUERY_LOAN_URL, {"loan-status" : "new"}) 
        loan_status_new = res.json()
        loan_status_approved = self.client.get(QUERY_LOAN_URL, {"loan-status" : "approved"}).json()
        loan_status_rejected = self.client.get(QUERY_LOAN_URL, {"loan-status": "rejected"}).json()

        self.assertEqual(len(loan_status_approved['loans']), 1)
        self.assertEqual(len(loan_status_new['loans']), 1)
        self.assertEqual(len(loan_status_rejected['loans']), 1)

    # def test_filter_by_all_params(self):
    #     pass
