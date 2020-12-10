from django.db import models
from app.settings import SECRET_KEY
import hashlib

class User(models.Model):
    email = models.EmailField(max_length=100, unique=True)
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

class Loan(models.Model):
    created_for = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agent')
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin')
    is_approved = models.BooleanField(default=False)
    principal_amount = models.IntegerField(default=0)
    interest_rate = models.FloatField(default=0.0)
    tenure_months = models.IntegerField(default=0)
    emi = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    STATUS = [
        ('new','new'),
        ('rejected','rejected'),
        ('approved', 'approved')
    ]    
    status = models.CharField(max_length=10, default='new', choices=STATUS)
    # edit_history = 
    #one to many

# class EditLoanHistory(models.Model):
#     pass