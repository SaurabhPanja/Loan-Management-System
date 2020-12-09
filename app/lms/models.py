from django.db import models
from app.settings import SECRET_KEY
import hashlib

class User(models.Model):
    email = models.EmailField(max_length=100, primary_key=True)
    password_hash = models.CharField(max_length=300, blank=True)
    ROLE = [
        ('admin','admin'),
        ('customer','customer'),
        ('agent', 'agent')
    ]
    role = models.CharField(max_length=10, default='customer', choices=ROLE)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.email

    def save_password_hash(self, password):
        hash_obj = hashlib.sha256()
        hash_obj.update(str(password).encode('utf-8'))
        hash_obj.update(str(SECRET_KEY).encode('utf-8'))
        self.password_hash = hash_obj.hexdigest()
    
    def check_password(self, password):
        hash_obj = hashlib.sha256()
        hash_obj.update(str(password).encode('utf-8'))
        hash_obj.update(str(SECRET_KEY).encode('utf-8'))   
        return self.password_hash == hash_obj.hexdigest()
    
    def create_user(self, email, password, role="customer"):
        self.email = email
        self.validate_unique()
        self.save_password_hash(password=password)
        self.role = role
        if role == "customer":
            self.is_active = True
        self.save()