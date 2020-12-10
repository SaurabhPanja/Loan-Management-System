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