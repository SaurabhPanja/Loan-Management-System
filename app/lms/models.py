from django.db import models
from app.settings import SECRET_KEY
import hashlib
from django.db.models.signals import pre_save
from django.dispatch import receiver

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