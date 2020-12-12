from django.http import JsonResponse
from lms.models import User, Loan, EditLoanHistory
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
from .create_loan import calculate_emi

@authorize_user
def edit_loan(request, id):
    if request.method == 'POST':
        error = False
        try:
            loan_id = id
            principal_amount = request.POST.get('principal-amount', '')
            interest_rate = request.POST.get('interest-rate', '')
            tenure = request.POST.get('tenure-months', '')
            loan_status = request.POST.get('status', '')
            
            encoded = request.META.get('HTTP_AUTHORIZATION', '')
            email, role = decode_token(encoded)

            if role == 'agent':
                loan_obj = Loan.objects.filter(pk=loan_id)
                
                if loan_obj.exists() and loan_obj.first().status != 'approved' and loan_status != 'approved':
                    loan_obj = loan_obj.first()
                else:
                    return bad_request()

                principal_amount = float(principal_amount)
                interest_rate = float(interest_rate)
                tenure = int(tenure)

                if principal_amount < 1 or interest_rate < 0 or interest_rate > 100 or tenure < 0:
                    return bad_request()

                EditLoanHistory.objects.create(
                    edit_history_of=loan_obj,
                    created_for=loan_obj.created_for,
                    created_by=loan_obj.created_by,
                    approved_by=loan_obj.approved_by,
                    is_approved=loan_obj.is_approved,
                    principal_amount=loan_obj.principal_amount,
                    interest_rate=loan_obj.interest_rate,
                    tenure_months=loan_obj.tenure_months,
                    emi=loan_obj.emi,
                    created_at=loan_obj.created_at,
                    status=loan_obj.status,
                )

                loan_obj.principal_amount = principal_amount or loan_obj.principal_amount
                loan_obj.interest_rate = interest_rate or loan_obj.interest_rate
                loan_obj.tenure_months = tenure or loan_obj.tenure_months
                loan_obj.status = loan_status or loan_obj.status

                emi = calculate_emi(loan_obj.principal_amount , loan_obj.interest_rate, loan_obj.tenure_months)

                loan_obj.emi = emi
                loan_obj.save()

                return JsonResponse({'message': 'Loan edited.'}, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse({'message': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        except ValueError:
            return bad_request()
        except Exception as e:
            dprint(e)
            error = True
            excpetion_log()

        if error:
            return internal_server_error()
    else:
        return bad_request()