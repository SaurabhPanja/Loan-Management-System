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
from django.utils import timezone
import pytz

@authorize_user
def query_loan(request):
    if request.method == 'GET':
        error = False
        try:
            encoded = request.META.get('HTTP_AUTHORIZATION', '')
            email, role = decode_token(encoded)
            
            loan_obj = []
            #query params
            created_date = request.GET.get('created-date', '')
            updated_date = request.GET.get('updated-date', '')
            loan_status = request.GET.get('loan-status', '')

            if role == 'customer':
                customer = User.objects.get(email=email)
                loan_obj = Loan.objects.filter(created_for=customer)
            else:
                loan_obj = Loan.objects.all()

            filtered_loan_arr = []
            if created_date:
                dd, mm, yy = created_date.split('/')
                created_date_start = datetime(int(yy), int(mm), int(dd), 0, 0, 0, tzinfo=pytz.utc)
                created_date_end = created_date_start + timedelta(hours=24)

                loan_obj = loan_obj.filter(created_at__range=(created_date_start, created_date_end)).order_by("-created_at")
            elif updated_date:
                dd, mm, yy = updated_date.split('/')
                updated_date_start = datetime(int(yy), int(mm), int(dd), 0, 0, 0, tzinfo=pytz.utc)
                updated_date_end = updated_date_start + timedelta(hours=24)

                loan_obj = loan_obj.filter(updated_at__range=(updated_date_start, updated_date_end)).order_by("-updated_at")
            elif loan_status:
                loan_obj = loan_obj.filter(status=loan_status)
            

            for loan in loan_obj:
                filtered_loan_arr.append(
                    {
                        'id': loan.id,
                        'customer' : loan.created_for.email,
                        'created_by' : loan.created_by.email,
                        'approved_by' : loan.approved_by.email if loan.approved_by else "not approved",
                        'principal_amount' : loan.principal_amount,
                        'interest_rate': loan.interest_rate,
                        'tenure_months' : loan.tenure_months,
                        'emi' : loan.emi,
                        'created_at' : loan.created_at,
                        'updated_at' : loan.updated_at,
                        'status' : loan.status
                    }
                )

            return JsonResponse(
                {
                    'loans': filtered_loan_arr,
                }, status=status.HTTP_200_OK)

        except:
            error = True
            excpetion_log()

        if error:
            return internal_server_error()
    else:
        return bad_request()    