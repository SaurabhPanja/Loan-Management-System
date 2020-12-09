from django.test import TestCase
from lms.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import re
from lms.views import dprint
import time
from pprint import pprint
from .helper_setUp_func import setUp_users

class UserApiTest(TestCase):
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
    
    #status_change without login
    def test_status_change_without_login(self):
        status_change_url = reverse('lms:change_user_status', kwargs={'id': self.admin_2.id})
        res = self.client.post(status_change_url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_status_change_admin_by_admin(self):
        """admin_1 is active, admin_1 will status_change admin_2"""

        self.assertFalse(self.admin_2.is_active)

        status_change_url = reverse('lms:change_user_status', kwargs={'id': self.admin_2.id})

        self.client.credentials(HTTP_AUTHORIZATION=self.admin_login_token)
        res = self.client.post(status_change_url)
        admin_2 = User.objects.get(pk=self.admin_2.id)
        self.assertTrue(admin_2.is_active)
        self.assertEqual(res.status_code,status.HTTP_202_ACCEPTED)

    #status_change user doesn't exist
    def test_status_change_non_existent_user(self):
        status_change_url = reverse('lms:change_user_status', kwargs={'id': 999})
        self.client.credentials(HTTP_AUTHORIZATION=self.admin_login_token)
        res = self.client.post(status_change_url)

        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_status_change_admin_by_agent(self):
        self.assertFalse(self.admin_2.is_active)

        status_change_url = reverse('lms:change_user_status', kwargs={'id': self.admin_2.id})

        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.post(status_change_url)
        admin_2 = User.objects.get(pk=self.admin_2.id)
        self.assertFalse(admin_2.is_active)
        self.assertEqual(res.status_code,status.HTTP_403_FORBIDDEN)        

    def test_status_change_agent_by_customer(self):
        self.assertFalse(self.agent_2.is_active)

        status_change_url = reverse('lms:change_user_status', kwargs={'id': self.agent_2.id})

        self.client.credentials(HTTP_AUTHORIZATION=self.customer_login_token)
        res = self.client.post(status_change_url)
        agent_2 = User.objects.get(pk=self.agent_2.id)
        self.assertFalse(agent_2.is_active)
        self.assertEqual(res.status_code,status.HTTP_403_FORBIDDEN)  

    def test_status_change_agent_by_agent(self):
        self.assertFalse(self.agent_2.is_active)

        status_change_url = reverse('lms:change_user_status', kwargs={'id': self.agent_2.id})

        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.post(status_change_url)
        agent_2 = User.objects.get(pk=self.agent_2.id)
        self.assertFalse(agent_2.is_active)
        self.assertEqual(res.status_code,status.HTTP_403_FORBIDDEN)          

    def test_status_change_admin_by_customer(self):
        self.assertFalse(self.admin_2.is_active)

        status_change_url = reverse('lms:change_user_status', kwargs={'id': self.admin_2.id})

        self.client.credentials(HTTP_AUTHORIZATION=self.customer_login_token)
        res = self.client.post(status_change_url)
        admin_2 = User.objects.get(pk=self.admin_2.id)
        self.assertFalse(admin_2.is_active)
        self.assertEqual(res.status_code,status.HTTP_403_FORBIDDEN)        

    def test_status_change_customer_by_agent(self):
        customer_status = self.customer_2.is_active

        status_change_url = reverse('lms:change_user_status', kwargs={'id': self.customer_2.id})

        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.post(status_change_url)
        customer_2 = User.objects.get(pk=self.customer_2.id)
        self.assertTrue(customer_2.is_active != customer_status)
        self.assertEqual(res.status_code,status.HTTP_202_ACCEPTED) 

    def test_status_change_customer_by_admin(self):
        customer_status = self.customer_2.is_active

        status_change_url = reverse('lms:change_user_status', kwargs={'id': self.customer_2.id})

        self.client.credentials(HTTP_AUTHORIZATION=self.admin_login_token)
        res = self.client.post(status_change_url)
        customer_2 = User.objects.get(pk=self.customer_2.id)
        self.assertTrue(customer_2.is_active != customer_status)
        self.assertEqual(res.status_code,status.HTTP_202_ACCEPTED) 

    def test_status_change_customer_by_customer(self):
        current_status = self.customer_2.is_active

        status_change_url = reverse('lms:change_user_status', kwargs={'id': self.customer_2.id})

        self.client.credentials(HTTP_AUTHORIZATION=self.customer_login_token)
        res = self.client.post(status_change_url)
        customer_2 = User.objects.get(pk=self.customer_2.id)
        self.assertTrue(customer_2.is_active == current_status)
        self.assertEqual(res.status_code,status.HTTP_403_FORBIDDEN) 

    # def test_edit_customer_by_customer(self):
    #     pass

    # def test_edit_customer_by_agent(self):
    #     pass

    # def test_edit_customer_by_admin(self):
    #     pass

    # def test_edit_admin_by_customer(self):
    #     pass

    # def test_edit_agent_by_customer(self):
    #     pass

    # def test_edit_agent_by_agent(self):
    #     pass

    # def test_get_a_user_by_customer(self):
    #     pass

    # def test_get_a_user_by_agent(self):
    #     pass

    # def test_get_a_user_by_admin(self):
    #     pass