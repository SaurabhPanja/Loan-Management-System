from rest_framework.test import APIClient
from lms.models import User
from django.urls import reverse

LOGIN_URL = reverse('lms:login')

def setUp_users():
    client = APIClient()

    customer_1 = User()
    customer_1.create_user(email="testing@token.com", password="goodpassword")
    customer_2 = User()
    customer_2.create_user(email="customer2@app.com", password="toogoodpassword")

    agent_1 = User()
    agent_1.is_active = True
    agent_1.create_user(email="agent@vinod.com", password="bunglekepechehaitaal", role="agent")
    agent_2 = User()
    agent_2.create_user(email="agent@sharekhan.com", password="wholetthedogsout", role="agent")

    admin_1 = User()
    admin_1.is_active = True
    admin_1.create_user(email="nice@admin.com", password="isadminnow", role="admin")
    admin_2 = User()
    admin_2.create_user(email="verynice@admin.com", password="wowniceadmin", role="admin")     

    #login
    cutomer_login_payload = {
        'email' : "testing@token.com",
        'password' : "goodpassword"
    }
    res = client.post(LOGIN_URL, cutomer_login_payload)
    customer_login_token = res.json().get('access-token')    

    admin_login_payload = {
        'email' : 'nice@admin.com',
        'password' : 'isadminnow'
    }      

    res = client.post(LOGIN_URL, admin_login_payload)
    admin_login_token = res.json().get('access-token')

    agent_login_payload = {
        'email' : 'agent@vinod.com',
        'password' : 'bunglekepechehaitaal'
    }            
    res = client.post(LOGIN_URL, agent_login_payload)
    agent_login_token = res.json().get('access-token')    

    return customer_login_token, agent_login_token, admin_login_token