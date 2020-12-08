from django.http import JsonResponse
from lms.models import User
from rest_framework import status
import jwt
from app.settings import SECRET_KEY
from datetime import datetime, timedelta
import os
import sys
import json
import re

def internal_server_error():
    response = {
        'message' : 'Internal server error.',
        'status' : status.HTTP_500_INTERNAL_SERVER_ERROR
    }
    return JsonResponse(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    

def validate_token(token):
    pass

def excpetion_log():
    print("****************************")
    exception_type, exception_object, exception_traceback = sys.exc_info()
    filename = exception_traceback.tb_frame.f_code.co_filename
    line_number = exception_traceback.tb_lineno
    print("Exception type: ", exception_type)
    print("File name: ", filename)
    print("Line number: ", line_number)
    print("****************************")    

def dprint(str):
    print("*"*100)
    print(str)
    print("*"*100)

def bad_request():
    response = {
        'message' : 'Bad Request'
    }

    return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)

def check_email(email):
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'

    return re.search(regex,email)

#users api
def create_user(request):
    error = False
    if request.method == "POST":
        try:
            request_data = request.POST       

            if 'email' in request_data and 'password' in request_data:
                if  not check_email(request_data['email']):
                    return JsonResponse({'message' : 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)

                if len(request_data['password']) < 8:
                    return JsonResponse({'message' : 'password too short'}, status=status.HTTP_400_BAD_REQUEST)
                    
                new_user = User()
                new_user.email = request_data['email']
                new_user.save_password_hash(request_data['password'])
                new_user.role = 'customer'
                if request_data['role'] == 'customer':
                    new_user.is_active = True    
                new_user.save()
            else:
                return bad_request()

        except:
            error = True
            excpetion_log()
        
        if error:
            return internal_server_error()
        else:
            response = {
                'message' : 'New user created',
                'status' : status.HTTP_201_CREATED
            }

            return JsonResponse(response, status=status.HTTP_201_CREATED)
    else:
        pass

def login(request):
    error = False
    if request.method == "POST":
        try:
            request_data = request.POST
            email = request_data.get('email','')
            password = request_data.get('password','')

            user = User.objects.filter(email=email)
            if user.exists():
                user = user.first()
            else:
                return JsonResponse(
                    {
                        'message' : 'No user found, Please register and continue',
                    }, status=status.HTTP_404_NOT_FOUND)

            if user.check_password(password=password):
                encoded_jwt = jwt.encode(
                    {
                        'email': user.email,
                        'role' : user.role,
                        'exp' : datetime.utcnow() + timedelta(hours=24),
                        #expire token after one day.

                    },
                     SECRET_KEY, algorithm='HS256'
                     )

                response = {
                    'access-token' : encoded_jwt.decode('utf-8')
                }
                return JsonResponse(response, status=status.HTTP_202_ACCEPTED)                     
            else:
                response = {
                    'message' : 'Invalid Credentials',
                    'status' : status.HTTP_401_UNAUTHORIZED
                }

                return JsonResponse(response, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            error = True
            excpetion_log()

        
        if error:
            return internal_server_error()




