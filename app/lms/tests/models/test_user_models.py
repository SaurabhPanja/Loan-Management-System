from django.test import TestCase
from lms.models import User
from app.settings import SECRET_KEY
import hashlib


class UserModelTest(TestCase):
    email = "abc@gmail.com"
    password = "password123"

    def setUp(self):
        u = User()
        u.email = self.email
        u.save_password_hash(password=self.password)
        u.save()

    def test_user_created(self):
        self.assertEqual(self.email, User.objects.get(email=self.email).email)

    def test_password_hash(self):
        hash_obj = hashlib.sha256()
        hash_obj.update(str(self.password).encode('utf-8'))
        hash_obj.update(str(SECRET_KEY).encode('utf-8'))
        password_hash = hash_obj.hexdigest()

        self.assertEqual(password_hash, User.objects.get(email=self.email).password_hash)
    
    def test_check_password(self):
        u = User.objects.get(email=self.email)
        check_password_true = u.check_password(self.password)
        check_password_false = u.check_password("hakunamata")

        self.assertTrue(check_password_true)
        self.assertFalse(check_password_false)

    def test_admin_role(self):
        email = "xyv@gmail.com"

        User.objects.create(email=email, role='admin')
        u_admin = User.objects.get(email=email)
        self.assertEqual(u_admin.role, 'admin')

    def test_agent_role(self):
        email = "agent@gmail.com"

        User.objects.create(email=email, role='agent')
        u_agent = User.objects.get(email=email)

        self.assertEqual(u_agent.role,'agent')

    def test_customer_role(self):
        email = "customer@gmail.com"

        User.objects.create(email=email, role='customer')
        u_customer = User.objects.get(email=email)

        self.assertEqual(u_customer.role,'customer')


