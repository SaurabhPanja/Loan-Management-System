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

# APPROVE_URL = reverse('lms:approve_user')

# class UserApiTest(TestCase):
#     def setUp(self):
#         self.client = APIClient()     

#         self.customer_login_token , self.agent_login_token, self.admin_login_token = setUp_users()

#     def test_approve_admin_by_admin(self):
#         all_admins = User.objects.filter(role='admim')
#         admin_1 = all_admins.first()
#         admin_2 = all_admins.last()
#         #making admin_2 active
#         admin_2.is_active = True
#         admin_2.save()

#         self.assertFalse(admin_1.role)
#         self.ass

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