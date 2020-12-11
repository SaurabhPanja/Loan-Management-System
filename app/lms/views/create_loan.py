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
def create_loan(request):
    if request.method == 'POST':
        error = False
        try:
            customer_id = request.POST.get('customer-id', '')
            principal_amount = request.POST.get('principal-amount', '')
            interest_rate = request.POST.get('interest-rate', '')
            tenure = request.POST.get('tenure-months', '')

            if not (customer_id and principal_amount and interest_rate and tenure):
                return bad_request()
            
            encoded = request.META.get('HTTP_AUTHORIZATION', '')
            email, role = decode_token(encoded)

            if role == 'agent':
                customer = User.objects.filter(pk=customer_id)
                if customer.exists() and customer.first().role == 'customer' and customer.first().is_active:
                    customer = customer.first()
                else:
                    return JsonResponse({
                        'message' : 'No such customer exists'
                    }, status=status.HTTP_400_BAD_REQUEST)

                principal_amount = float(principal_amount)
                interest_rate = float(interest_rate)
                tenure = int(tenure)

                if principal_amount < 1 or interest_rate < 0 or interest_rate > 100 or tenure < 0:
                    return bad_request()

                emi = calculate_emi(principal_amount, interest_rate, tenure)

                Loan.objects.create(
                    created_for=customer,
                    created_by=User.objects.get(email=email),
                    principal_amount=principal_amount,
                    interest_rate=interest_rate,
                    tenure_months = tenure,
                    emi = emi
                )

                return JsonResponse({'message': 'Loan created.'}, status=status.HTTP_201_CREATED)
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

def calculate_emi(principal_amount, interest_rate, tenure):
    emi = (principal_amount * (interest_rate / 100) * (1 + (interest_rate / 100))**tenure) / ((1 + (interest_rate/ 100 ))**tenure - 1)

    return round(emi, 2)