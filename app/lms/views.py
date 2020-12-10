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
from django.core.exceptions import ValidationError
from pprint import pprint
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse

def internal_server_error():
    response = {
        'message' : 'Internal server error.',
        'status' : status.HTTP_500_INTERNAL_SERVER_ERROR
    }
    return JsonResponse(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    

def validate_token(token):
    pass

def excpetion_log():
    print("\n****************************")
    exception_type, exception_object, exception_traceback = sys.exc_info()
    filename = exception_traceback.tb_frame.f_code.co_filename
    line_number = exception_traceback.tb_lineno
    print("Exception type: ", exception_type)
    print("File name: ", filename)
    print("Line number: ", line_number)
    print("****************************")    

def dprint(str):
    print("\n")
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

def decode_token(encoded):
        decoded = jwt.decode(encoded, SECRET_KEY, algorithms=['HS256'])
        email = decoded['email']
        role = decoded['role']   

        return email, role 

def authorize_user(func):
    def wrap(request, *args, **kwargs):
        encoded = request.META.get('HTTP_AUTHORIZATION', '')
        try:
            jwt.decode(encoded, SECRET_KEY, algorithms=['HS256'])
        except Exception as e:
            return JsonResponse({'message' : 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)        

        return func(request, *args, **kwargs)
    
    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    
    return wrap

def json_user_obj(user):
    return {
        'id' : user.id,
        'email' : user.email,
        'role' : user.role,
        'is_active' : user.is_active
    }

@authorize_user
def get_user(request, id):
    if request.method == "GET":
        error = False
        try:
            encoded = request.META.get('HTTP_AUTHORIZATION', '')
            email, role = decode_token(encoded)

            queried_user = User.objects.filter(pk=id)

            if queried_user.exists():
                queried_user = queried_user.first()
            else:
                return JsonResponse(
                    {
                        'message' : 'No user found. Bad Request',
                    }, status=status.HTTP_400_BAD_REQUEST)      

            # dprint(queried_user.email)
            
            if role == 'admin':
                return JsonResponse({
                    'user' : json_user_obj(queried_user)
                }, status=status.HTTP_200_OK)
            
            if role == 'agent' and ( queried_user.role == 'customer' or queried_user.email == email):
                return JsonResponse({
                    'user' : json_user_obj(queried_user)
                }, status=status.HTTP_200_OK)       

            if role == 'customer' and queried_user.email == email:
                return JsonResponse({
                    'user' : json_user_obj(queried_user)
                }, status=status.HTTP_200_OK)   

            return JsonResponse(
                {
                    'message' : 'Forbidden request'
                }, status=status.HTTP_403_FORBIDDEN
            )                        


        except Exception as e:
            dprint(e)
            error = True
            excpetion_log()            

        if error:
            return internal_server_error()

    else:
        return bad_request()


@authorize_user
def edit_user(request, id):
    if request.method == "POST":
        error = False
        try:
            encoded = request.META.get('HTTP_AUTHORIZATION', '')
            to_edit_email = request.POST.get('email','')
            to_edit_is_active = request.POST.get('is_active','')

            if not to_edit_email and not to_edit_is_active:
                return JsonResponse({'message': 'Bad Request. All values are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            to_edit_is_active = True if to_edit_is_active.lower() == 'true' else False

            email, role = decode_token(encoded)
            to_approve_user = User.objects.filter(pk=id)

            if to_approve_user.exists():
                to_approve_user = to_approve_user.first()
            else:
                return JsonResponse(
                    {
                        'message' : 'No user found to approve. Bad Request',
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            if role == 'admin':
                to_approve_user.email = to_edit_email
                to_approve_user.is_active = to_edit_is_active
            elif role == 'agent' and to_approve_user.role == 'customer':
                to_approve_user.email = to_edit_email
                to_approve_user.is_active = to_edit_is_active
            else:
                return JsonResponse({'message': 'Invalid request'}, status=status.HTTP_403_FORBIDDEN)

            to_approve_user.save()
            return JsonResponse({'message': 'User approved'}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            dprint(e)
            error = True
            excpetion_log()
        
        if error:
            return internal_server_error()
    else:
        return bad_request()
        

#users api
def create_or_get_user(request):
    error = False
    if request.method == "POST":
        try:
            request_data = request.POST       

            if 'email' in request_data and 'password' in request_data and 'role' in request_data:
                email = request_data['email']
                password = request_data['password']
                role = request_data.get('role')

                if role not in ['admin', 'customer', 'agent']:
                    return JsonResponse({'message': 'Invliad role'}, status=status.HTTP_400_BAD_REQUEST)

                if  not check_email(email):
                    return JsonResponse({'message' : 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)

                if len(password) < 8:
                    return JsonResponse({'message' : 'password should be more than 8 characters'}, status=status.HTTP_400_BAD_REQUEST)

                new_user = User()
                new_user.create_user(email=email, password=password, role=role)
            else:
                return bad_request()
        
        except ValidationError as e:
            return JsonResponse({
                'message' : e.messages[0]
            }, status=status.HTTP_409_CONFLICT)

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
    elif request.method == "GET":
        encoded = request.META.get('HTTP_AUTHORIZATION', '')
        try:
            email, role = decode_token(encoded)
            if role == 'customer':
                return JsonResponse({'message' : 'Invalid Request. Unauthorized.'}, status=status.HTTP_401_UNAUTHORIZED)
            elif role == 'agent':
                all_users = User.objects.filter(Q(role='customer') | Q(role='agent')).values('email', 'role','is_active')
            elif role == 'admin':
                all_users = User.objects.all().values('email', 'role', 'is_active')
            
            response = {
                'users' : list(all_users),
            }

            return JsonResponse(response, status=status.HTTP_200_OK)
        except Exception as e:
            # dprint(e)
            return JsonResponse({'message' : 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)


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
                if not user.is_active:
                    return JsonResponse({
                        'message' : 'User is not active'
                    }, status=status.HTTP_403_FORBIDDEN)
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
    else:
        return bad_request()





