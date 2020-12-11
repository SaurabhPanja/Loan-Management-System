from django.http import JsonResponse
from lms.models import User, Loan
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
def approve_loan(request, id):
    if request.method == 'POST':
        error = False
        try:
            loan_id = id
            encoded = request.META.get('HTTP_AUTHORIZATION', '')
            email, role = decode_token(encoded)

            if role == 'admin':
                loan_obj = Loan.objects.filter(pk=loan_id)
                if loan_obj.exists():
                    loan_obj = loan_obj.first()
                else:
                    return bad_request()
                
                admin_user = User.objects.get(email=email)
                loan_obj.approved_by = admin_user
                loan_obj.is_approved=True
                loan_obj.status='approved'
                loan_obj.save()

                return JsonResponse({'message': 'Loan approved'}, status=status.HTTP_202_ACCEPTED)

            else:
                return JsonResponse({'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        except:
            error = True
            excpetion_log()

        if error:
            return internal_server_error()
    else:
        return bad_request()