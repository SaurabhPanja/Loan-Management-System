from django.test import TestCase
from lms.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import re
from lms.utils import dprint
import time
from pprint import pprint
from .helper_setUp_func import setUp_users

class UserApiTest(TestCase):
    """Test suite for authorizing roles"""
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

        self.admin_edit_payload = {
            'email' : 'edited@admin.com',
            'is_active' : True
        }

        self.agent_edit_payload = {
            'email' : 'edited@agent.com',
            'is_active' : True
        }
        self.customer_edit_payload = {
            'email' : 'edited@customer.com',
            'is_active' : False
        }                

    
    #edit without login
    def test_edit_without_login(self):
        edit_url = reverse('lms:edit_user', kwargs={'id': self.admin_2.id})
        res = self.client.post(edit_url, self.customer_edit_payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_edit_admin_by_admin(self):
        """admin_1 is active, admin_1 will edit admin_2"""

        self.assertFalse(self.admin_2.is_active)

        edit_url = reverse('lms:edit_user', kwargs={'id': self.admin_2.id})

        self.client.credentials(HTTP_AUTHORIZATION=self.admin_login_token)
        res = self.client.post(edit_url, self.admin_edit_payload)
        admin_2 = User.objects.get(pk=self.admin_2.id)

        self.assertEqual(admin_2.email, self.admin_edit_payload['email'])
        self.assertTrue(admin_2.is_active)
        self.assertEqual(res.status_code,status.HTTP_202_ACCEPTED)

    #edit user doesn't exist
    def test_edit_non_existent_user(self):
        edit_url = reverse('lms:edit_user', kwargs={'id': 999})
        self.client.credentials(HTTP_AUTHORIZATION=self.admin_login_token)
        res = self.client.post(edit_url)

        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_empty_edit_payload(self):
        edit_url = reverse('lms:edit_user', kwargs={'id': self.customer_1.id})
        self.client.credentials(HTTP_AUTHORIZATION=self.admin_login_token)
        res = self.client.post(edit_url)

        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_edit_admin_by_agent(self):
        edit_url = reverse('lms:edit_user', kwargs={'id': self.admin_2.id})

        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.post(edit_url, self.admin_edit_payload)
        admin_2 = User.objects.get(pk=self.admin_2.id)
        
        self.assertEqual(admin_2.email, self.admin_2.email)
        self.assertEqual(admin_2.is_active, self.admin_2.is_active)
        self.assertEqual(res.status_code,status.HTTP_403_FORBIDDEN)        

    def test_edit_agent_by_customer(self):
        edit_url = reverse('lms:edit_user', kwargs={'id': self.agent_2.id})

        self.client.credentials(HTTP_AUTHORIZATION=self.customer_login_token)
        res = self.client.post(edit_url, self.agent_edit_payload)
        agent_2 = User.objects.get(pk=self.agent_2.id)

        self.assertEqual(agent_2.email, self.agent_2.email)
        self.assertEqual(agent_2.is_active, self.admin_2.is_active)
        self.assertEqual(res.status_code,status.HTTP_403_FORBIDDEN)  

    def test_edit_agent_by_agent(self):
        edit_url = reverse('lms:edit_user', kwargs={'id': self.agent_2.id})

        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.post(edit_url, self.agent_edit_payload)
        agent_2 = User.objects.get(pk=self.agent_2.id)

        self.assertEqual(agent_2.is_active, self.agent_2.is_active)
        self.assertEqual(agent_2.email, self.agent_2.email)
        self.assertEqual(res.status_code,status.HTTP_403_FORBIDDEN)          

    def test_edit_admin_by_customer(self):
        edit_url = reverse('lms:edit_user', kwargs={'id': self.admin_2.id})

        self.client.credentials(HTTP_AUTHORIZATION=self.customer_login_token)
        res = self.client.post(edit_url, self.admin_edit_payload)
        admin_2 = User.objects.get(pk=self.admin_2.id)

        self.assertEqual(admin_2.is_active, self.admin_2.is_active)
        self.assertEqual(admin_2.email, self.admin_2.email)
        self.assertEqual(res.status_code,status.HTTP_403_FORBIDDEN)        

    def test_edit_customer_by_agent(self):
        edit_url = reverse('lms:edit_user', kwargs={'id': self.customer_2.id})

        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.post(edit_url, self.customer_edit_payload)
        customer_2 = User.objects.get(pk=self.customer_2.id)

        self.assertEqual(customer_2.email, self.customer_edit_payload['email'])
        self.assertEqual(customer_2.is_active, self.customer_edit_payload['is_active'])
        self.assertEqual(res.status_code,status.HTTP_202_ACCEPTED) 

    def test_edit_customer_by_admin(self):
        edit_url = reverse('lms:edit_user', kwargs={'id': self.customer_2.id})

        self.client.credentials(HTTP_AUTHORIZATION=self.admin_login_token)
        res = self.client.post(edit_url, self.customer_edit_payload)
        customer_2 = User.objects.get(pk=self.customer_2.id)

        self.assertEqual(customer_2.email, self.customer_edit_payload['email'])
        self.assertEqual(customer_2.is_active, self.customer_edit_payload['is_active'])
        self.assertEqual(res.status_code,status.HTTP_202_ACCEPTED) 

    def test_edit_customer_by_customer(self):
        edit_url = reverse('lms:edit_user', kwargs={'id': self.customer_2.id})

        self.client.credentials(HTTP_AUTHORIZATION=self.customer_login_token)
        res = self.client.post(edit_url, self.customer_edit_payload)
        customer_2 = User.objects.get(pk=self.customer_2.id)

        self.assertEqual(customer_2.email, self.customer_2.email)
        self.assertEqual(customer_2.is_active, self.customer_2.is_active)
        self.assertEqual(res.status_code,status.HTTP_403_FORBIDDEN) 

    def test_get_user_as_customer(self):
        """A customer can only see their profile."""
        customer_self_url = reverse('lms:get_user', kwargs={'id': self.customer_1.id})
        customer_2_url = reverse('lms:get_user', kwargs={'id': self.customer_2.id})
        agent_url = reverse('lms:get_user', kwargs={'id': self.agent_1.id})
        admin_url = reverse('lms:get_user', kwargs={'id': self.admin_1.id})
        non_existent_user_url = reverse('lms:get_user', kwargs={'id': 999})
        
        self.client.credentials(HTTP_AUTHORIZATION=self.customer_login_token)

        customer_self_res = self.client.get(customer_self_url)
        customer_2_res = self.client.get(customer_2_url)
        agent_res = self.client.get(agent_url)
        admin_res = self.client.get(admin_url)
        non_existent_user_res = self.client.get(non_existent_user_url)

        self.assertEqual(customer_self_res.status_code, status.HTTP_200_OK)
        self.assertEqual(customer_2_res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(agent_res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(admin_res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(non_existent_user_res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_a_user_by_agent(self):
        """an agent can see only thier profile and all customers profiles."""
        customer_1_url = reverse('lms:get_user', kwargs={'id': self.customer_1.id})
        agent_self_url = reverse('lms:get_user', kwargs={'id': self.agent_1.id})
        agent_2_url = reverse('lms:get_user', kwargs={'id': self.agent_2.id})
        admin_url = reverse('lms:get_user', kwargs={'id': self.admin_1.id})
        non_existent_user_url = reverse('lms:get_user', kwargs={'id': 999})

        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)

        customer_1_res = self.client.get(customer_1_url)
        agent_self_res = self.client.get(agent_self_url)
        agent_2_res = self.client.get(agent_2_url)
        admin_res = self.client.get(admin_url)
        non_existent_user_res = self.client.get(non_existent_user_url)

        self.assertEqual(customer_1_res.status_code, status.HTTP_200_OK)
        self.assertEqual(agent_self_res.status_code, status.HTTP_200_OK)
        self.assertEqual(agent_2_res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(admin_res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(non_existent_user_res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_a_user_by_admin(self):
        """an admin can see only all profiles"""
        admin_self_url = reverse('lms:get_user', kwargs={'id': self.admin_1.id})
        admin_2_url = reverse('lms:get_user', kwargs={'id': self.admin_2.id})
        customer_1_url = reverse('lms:get_user', kwargs={'id': self.customer_1.id})
        agent_1_url = reverse('lms:get_user', kwargs={'id': self.agent_1.id})
        non_existent_user_url = reverse('lms:get_user', kwargs={'id': 999})

        self.client.credentials(HTTP_AUTHORIZATION=self.admin_login_token)        

        customer_1_res = self.client.get(customer_1_url)
        admin_self_res = self.client.get(admin_self_url)
        agent_1_res = self.client.get(agent_1_url)
        admin_2_res = self.client.get(admin_2_url)
        non_existent_user_res = self.client.get(non_existent_user_url)

        self.assertEqual(customer_1_res.status_code, status.HTTP_200_OK)
        self.assertEqual(admin_self_res.status_code, status.HTTP_200_OK)
        self.assertEqual(agent_1_res.status_code, status.HTTP_200_OK)
        self.assertEqual(admin_2_res.status_code, status.HTTP_200_OK)
        self.assertEqual(non_existent_user_res.status_code, status.HTTP_400_BAD_REQUEST)
