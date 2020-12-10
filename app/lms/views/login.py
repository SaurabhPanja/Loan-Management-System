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