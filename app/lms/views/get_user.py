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