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

class EditLoanTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.customer_login_token, self.agent_login_token, self.admin_login_token = setUp_users()

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

        self.edit_loan_request = {
            'principal-amount' : 50000,
            'interest-rate' : 3,
            'tenure-months' : 11
        }


        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        self.client.post(reverse('lms:create_loan'), self.customer_loan_request)  

        self.loan_edit_url = reverse('lms:edit_loan', kwargs={'id' : Loan.objects.last().id})

    def test_edit_loan_by_customer(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.customer_login_token)
        res = self.client.post(self.loan_edit_url, self.edit_loan_request)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_edit_loan_by_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.admin_login_token)
        res = self.client.post(self.loan_edit_url, self.edit_loan_request)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_edit_loan_by_agent(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.post(self.loan_edit_url, self.edit_loan_request)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)   

        loan_obj = Loan.objects.last()
        self.assertEqual(loan_obj.principal_amount, self.edit_loan_request['principal-amount'])     
        self.assertEqual(loan_obj.tenure_months, self.edit_loan_request['tenure-months'])
        self.assertEqual(loan_obj.interest_rate, self.edit_loan_request['interest-rate'])
        self.assertEqual(loan_obj.emi, 5403.87)

    def test_edit_non_existent_loan(self):
        non_existent_loan_edit_url = reverse('lms:edit_loan', kwargs={'id' : 878})
        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.post(non_existent_loan_edit_url, self.edit_loan_request)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_approved_loan(self):
        loan_obj = Loan.objects.last()
        loan_obj.status = 'approved'
        loan_obj.save()

        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.post(self.loan_edit_url, self.edit_loan_request)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_a_loan_by_agent(self):
        self.edit_loan_request['status'] = 'rejected'

        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.post(self.loan_edit_url, self.edit_loan_request)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)    
        self.assertEqual(Loan.objects.last().status, 'rejected')  

    def test_approve_a_loan_by_agent(self):
        self.edit_loan_request['status'] = 'approved'

        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.post(self.loan_edit_url, self.edit_loan_request)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)               

    def test_invalid_loan_request(self):
        invalid_loan_request = {
            'principal-amount' : "one lakh",
            'tenure-months' : "10 months",
            'interest_rate' : 4000,
        }

        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.post(self.loan_edit_url, invalid_loan_request)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)         

    def test_save_edited_loan(self):
        last_loan_obj = Loan.objects.last()
        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.post(self.loan_edit_url, self.edit_loan_request)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        edit_loan = EditLoanHistory.objects.last()

        self.assertEqual(edit_loan.principal_amount, last_loan_obj.principal_amount)
        self.assertEqual(edit_loan.interest_rate, last_loan_obj.interest_rate)
        self.assertEqual(edit_loan.tenure_months, last_loan_obj.tenure_months)
        self.assertEqual(edit_loan.emi, last_loan_obj.emi)
        self.assertEqual(edit_loan.status, last_loan_obj.status)
        self.assertEqual(edit_loan.created_at, last_loan_obj.created_at)
        self.assertEqual(edit_loan.created_for, last_loan_obj.created_for)
        self.assertEqual(edit_loan.created_by, last_loan_obj.created_by)
        self.assertEqual(edit_loan.approved_by, last_loan_obj.approved_by)
        

