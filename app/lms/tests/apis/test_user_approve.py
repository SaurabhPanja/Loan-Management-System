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

LOGIN_URL = reverse('lms:login')
# APPROVE_URL = reverse('lms:approve_user')

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

    def test_approve_admin_by_admin(self):
        pass

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