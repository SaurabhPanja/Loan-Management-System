from django.test import TestCase
from lms.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import jwt
from app.settings import SECRET_KEY

LOGIN_URL = reverse('lms:login')
USER_URL = reverse('lms:create_or_get_user')

class AuthApiTest(TestCase):
    customer_email = "customer@email.com"
    customer_password = "customer1"

    agent_email = "agent@email.com"
    agent_password = "agent1"

    admin_email = "admin@email.com"
    admin_password = "admin1"

    def setUp(self):
        customer_user = User()
        customer_user.email = self.customer_email
        customer_user.save_password_hash(password=self.customer_password)
        customer_user.role = 'customer'
        customer_user.is_active = True
        customer_user.save()

        admin_user = User()
        admin_user.email = self.admin_email
        admin_user.save_password_hash(password=self.admin_password)
        admin_user.role = 'admin'
        admin_user.is_active = True
        admin_user.save()    

        agent_user = User()
        agent_user.email = self.agent_email
        agent_user.save_password_hash(password=self.agent_password)
        agent_user.role = 'agent'
        agent_user.is_active = True
        agent_user.save()            

    def test_login_create_token(self):
        """Generate toke after login"""

        payload = {
            'email' : self.customer_email,
            'password' : self.customer_password,
        }
       
        res = self.client.post(LOGIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn("access-token", res.json())

    def test_login_user_not_exists(self):
        payload = {
            'email' : 'abc@gmail.com',
            'password' : 'mypass123',
        }

        res = self.client.post(LOGIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_wrong_password_create_token(self):
        payload = {
            'email' : self.agent_email,
            'password' : 'wrong_password',
        }

        res = self.client.post(LOGIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_is_customer(self):
        payload = {
            'email' : self.customer_email,
            'password' : self.customer_password,
        }
       
        res = self.client.post(LOGIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)

        access_token = res.json().get('access-token')
        decoded_token = jwt.decode(access_token, SECRET_KEY, algorithm='HS256')
        
        self.assertEqual('customer', decoded_token['role'])

    def test_user_is_admin(self):
        payload = {
            'email' : self.admin_email,
            'password' : self.admin_password,
        }
       
        res = self.client.post(LOGIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)

        access_token = res.json().get('access-token')
        decoded_token = jwt.decode(access_token, SECRET_KEY, algorithm='HS256')
        
        self.assertEqual('admin', decoded_token['role'])

    def test_user_is_agent(self):
        payload = {
            'email' : self.agent_email,
            'password' : self.agent_password,
        }
       
        res = self.client.post(LOGIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)

        access_token = res.json().get('access-token')
        decoded_token = jwt.decode(access_token, SECRET_KEY, algorithm='HS256')
        
        self.assertEqual('agent', decoded_token['role'])
    
    def test_generate_token_only_if_is_active_customer(self):
        new_customer_email = "newcustomer@gmail.com"
        new_customer_password = "password"
        new_customer = User()
        new_customer.email = new_customer_email
        new_customer.save_password_hash(new_customer_password)
        new_customer.is_active = False
        new_customer.save()

        payload = {
            'email' : new_customer_email,
            'password' : new_customer_password,
        }
       
        res = self.client.post(LOGIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_generate_token_only_if_is_active_agent(self):
        new_agent_email = "newagent@gmail.com"
        new_agent_password = "password"
        new_agent = User()
        new_agent.email = new_agent_email
        new_agent.save_password_hash(new_agent_password)
        new_agent.save()

        payload = {
            'email' : new_agent_email,
            'password' : new_agent_password,
        }
       
        res = self.client.post(LOGIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_generate_token_only_if_is_active_admin(self):
        new_admin_email = "newcustomer@gmail.com"
        new_admin_password = "password"
        new_admin = User()
        new_admin.email = new_admin_email
        new_admin.save_password_hash(new_admin_password)
        new_admin.save()

        payload = {
            'email' : new_admin_email,
            'password' : new_admin_password,
        }
       
        res = self.client.post(LOGIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)        




