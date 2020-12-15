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

from lms.utils import *

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
                return JsonResponse({'message': 'Invalid inputs'}, status=400)
        
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
        encoded = encoded.split(' ')[-1] if encoded else ''
        try:
            email, role = decode_token(encoded)
            if role == 'customer':
                return JsonResponse({'message' : 'Invalid Request. Unauthorized.'}, status=status.HTTP_401_UNAUTHORIZED)
            elif role == 'agent':
                all_users = User.objects.filter(Q(role='customer') | Q(role='agent')).values('email', 'role','is_active')
            elif role == 'admin':
                all_users = User.objects.all().values('email', 'role', 'is_active', 'id')
            
            response = {
                'users' : list(all_users),
            }

            return JsonResponse(response, status=status.HTTP_200_OK)
        except Exception as e:
            # dprint(e)
            return JsonResponse({'message' : 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)