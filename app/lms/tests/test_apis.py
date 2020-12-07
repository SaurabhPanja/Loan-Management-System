from django.test import TestCase
from lms.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('lms:create_user')

class UserApiTest(TestCase):
    customer_email = "customer@email.com"
    customer_password = "customer1"

    agent_email = "agent@email.com"
    agent_password = "agent1"

    admin_email = "admin@email.com"
    admin_password = "admin1"

    def setUp(self):
        self.client = APIClient()

    def test_create_new_user_customer(self):
        payload = {
            'email' : self.customer_email,
            'password' : self.customer_password,
            'role' : 'customer'
        }

        res = self.client.post(CREATE_USER_URL, payload)

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

        res = self.client.post(CREATE_USER_URL, payload)

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

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email=self.admin_email)

        self.assertTrue(user)
        self.assertTrue(user.check_password(payload['password']))
        self.assertFalse(user.is_active)

    # def test_all_users_get_as_customer(self):
    #     factory = APIRequestFactory()
    #     request = factory.get('/users/',{
    #         'email' : self.customer_email,
    #         'password' : self.customer_password,
    #     })
    #     print(dir(request))
    #     self.assertEqual(1,1)

    # def test_all_users_get_as_agent(self):
    #     pass

    # def test_all_users_get_as_admin(self):
    #     pass


    # def test_approve_agent_by_admin(self):
    #     pass
    
    # def test_approve_admin_by_admin(self):
    #     pass

    # def test_approve_admin_by_agent(self):
    #     pass

    # def test_approve_agent_by_customer(self):
    #     pass

    # def test_approve_agent_by_agent(self):
    #     pass

    # def test_approve_admin_by_customer(self):
    #     pass

    # def test_approve_customer_by_agent(self):
    #     pass

    # def test_approve_customer_by_admin(self):
    #     pass

    # def test_approve_customer_by_customer(self):
    #     pass

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




