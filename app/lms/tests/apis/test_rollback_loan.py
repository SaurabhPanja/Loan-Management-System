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

class RollbackLoanTest(TestCase):
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

        self.old_loan_obj = Loan.objects.last()

        self.loan_edit_url = reverse('lms:edit_loan', kwargs={'id' : Loan.objects.last().id})
        self.client.post(self.loan_edit_url, self.edit_loan_request)

        self.rollback_url = reverse('lms:rollback_loan', kwargs={'loan_id':Loan.objects.last().id, 'edit_id': EditLoanHistory.objects.last().id})

    def test_rollback_by_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.admin_login_token)
        res = self.client.post(self.rollback_url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_rollback_by_customer(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.customer_login_token)
        res = self.client.post(self.rollback_url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)        

    def test_rollback_by_agent(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.post(self.rollback_url)

        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)
        loan_obj = Loan.objects.last()
        self.assertEqual(self.old_loan_obj.principal_amount, loan_obj.principal_amount)
        self.assertEqual(self.old_loan_obj.tenure_months, loan_obj.tenure_months)
        self.assertEqual(self.old_loan_obj.emi, loan_obj.emi)
        self.assertEqual(self.old_loan_obj.interest_rate, loan_obj.interest_rate)
    
    def test_non_existent_loan_rollback(self):
        invalid_loan_url = reverse('lms:rollback_loan', kwargs={'loan_id':778, 'edit_id': 1})
        res = self.client.post(invalid_loan_url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_rollback_request(self):
        """Invalid loan as in rollback to othe loan's previous edited version"""
        new_loan_request = {
            'customer-id' : self.customer_1.id,
            'principal-amount' : "3500",
            'interest-rate' : "4",
            'tenure-months' : "12"
        }

        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        self.client.post(reverse('lms:create_loan'), new_loan_request)

        self.loan_edit_url = reverse('lms:edit_loan', kwargs={'id' : Loan.objects.last().id})
        self.client.post(self.loan_edit_url, self.edit_loan_request)

        loan_obj_id = Loan.objects.first().id
        other_loan_edit_obj_id = EditLoanHistory.objects.last().id

        res = self.client.post(reverse('lms:rollback_loan', kwargs={'loan_id': loan_obj_id, 'edit_id': other_loan_edit_obj_id}))

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rollback_approved_loan(self):
        """An approved loan should not be rollbacked to any previous version"""
        loan_obj_id = Loan.objects.last().id
        approve_loan_url = reverse('lms:approve_loan' , kwargs={'id' : loan_obj_id})
        self.client.credentials(HTTP_AUTHORIZATION=self.admin_login_token)
        self.client.post(approve_loan_url)

        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.post(self.rollback_url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    