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

USER_URL = reverse('lms:create_or_get_user')
LOGIN_URL = reverse('lms:login')

class UserApiTest(TestCase):
    customer_email = "customer@email.com"
    customer_password = "customer1"

    agent_email = "agent@email.com"
    agent_password = "agent1234"

    admin_email = "admin@email.com"
    admin_password = "admin1234"    

    def setUp(self):
        self.client = APIClient()

        self.customer_login_token , self.agent_login_token, self.admin_login_token = setUp_users()

    def test_create_new_user_customer(self):
        payload = {
            'email' : self.customer_email,
            'password' : self.customer_password,
            'role' : 'customer'
        }

        res = self.client.post(USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)    

        user = User.objects.get(email=self.customer_email)

        self.assertTrue(user)
        self.assertTrue(user.check_password(payload['password']))
        self.assertTrue(user.is_active)

    def test_create_new_user_agent(self):
        payload = {
            'email' : self.agent_email,
            'password' : self.agent_password,
            'role' : 'agent'
        }

        res = self.client.post(USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        
        user = User.objects.get(email=self.agent_email)
        
        self.assertTrue(user)
        self.assertTrue(user.check_password(payload['password']))
        self.assertFalse(user.is_active)
    
    def test_create_new_user_admin(self):
        payload = {
            'email' : self.admin_email,
            'password' : self.admin_password,
            'role' : 'admin'
        }

        res = self.client.post(USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email=self.admin_email)

        self.assertTrue(user)
        self.assertTrue(user.check_password(payload['password']))
        self.assertFalse(user.is_active)
    
    def test_user_already_exists(self):
        payload = {
            'email' : "testing@token.com",
            'password' : self.customer_password,
            'role' : 'customer'
        }

        res = self.client.post(USER_URL, payload)

        #ERROR USER ALREADY EXISTS
        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)


    def test_create_new_user_error(self):
        payload = {}

        res = self.client.post(USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_short_password(self):
        payload = {
            'email' : 'invalid@pasword.com',
            'password' : '123',
            'role' : 'admin'
        }        

        res = self.client.post(USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_email(self):
        payload = {
            'email' : 'saurabhpanja',
            'password' : 'strongpassword',
            'role' : 'customer'
        }

        res = self.client.post(USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_role(self):
        payload = {
            'email' : 'invalid@role.com',
            'password' : 'strongpassword',
            'role' : 'invalid role'
        }

        res = self.client.post(USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    

    def test_all_users_get_as_customer(self):
        """Customer should not be able to see all the users"""

        self.client.credentials(HTTP_AUTHORIZATION=self.customer_login_token)
        res = self.client.get(USER_URL)

        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)

    def test_invalid_users_api_request(self):
        self.client.credentials(HTTP_AUTHORIZATION="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6ImFkbWluQGdtYWlsLmNvbSIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTYwNzU5NzIwM30.19P-by_Xc2oeAVIlZ9Zgf6YbcaseSq_fWcgzPgVsfCp")
        res = self.client.get(USER_URL)

        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)        

    def test_all_users_get_as_agent(self):
        """Agent can see all customers and agents, but not admin"""
        self.client.credentials(HTTP_AUTHORIZATION=self.agent_login_token)
        res = self.client.get(USER_URL)

        response_data = res.json()

        all_users = response_data.get('users')
        admin_present = False
        no_of_users = len(all_users)

        for user in all_users:
            if user['role'] == 'admin':
                admin_present = True

        self.assertEqual(res.status_code,status.HTTP_200_OK)    
        self.assertFalse(admin_present)   
        self.assertEqual(no_of_users, 4) 

    def test_all_users_get_as_admin(self):
        """Admin can see all customers, agents and admins"""
        self.client.credentials(HTTP_AUTHORIZATION=self.admin_login_token)
        res = self.client.get(USER_URL)
        response_data = res.json()
        
        all_users = response_data.get('users')
        no_of_users = len(all_users)        

        self.assertEqual(res.status_code,status.HTTP_200_OK)     
        self.assertEqual(no_of_users, 6)     


    def test_approve_agent_by_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.admin_login_token)





