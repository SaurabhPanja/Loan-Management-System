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

@authorize_user
def rollback_loan(request, loan_id, edit_id):
    if request.method == 'POST':
        error = False
        try:
            encoded = request.META.get('HTTP_AUTHORIZATION', '')
            email, role = decode_token(encoded)

            if role == 'agent':
                loan_obj = Loan.objects.filter(pk=loan_id)
                loan_edit_obj = EditLoanHistory.objects.filter(pk=edit_id)
                if loan_obj.exists() and loan_edit_obj.exists():
                    loan_obj = loan_obj.first()
                    loan_edit_obj = loan_edit_obj.first()
                    if loan_edit_obj.edit_history_of.id != loan_obj.id or loan_obj.is_approved:
                        # dprint(loan_obj.is_approved)
                        return bad_request()

                else:
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

                loan_obj.principal_amount =  loan_edit_obj.principal_amount
                loan_obj.interest_rate = loan_edit_obj.interest_rate
                loan_obj.tenure_months = loan_edit_obj.tenure_months
                loan_obj.status = loan_edit_obj.status
                loan_obj.emi = loan_edit_obj.emi
                loan_obj.save()

                return JsonResponse({'message': 'Loan roll backed to edit id '  + str(loan_edit_obj.id)}, status=status.HTTP_202_ACCEPTED)

            else:
                return JsonResponse({'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        except:
            error = True
            excpetion_log()

        if error:
            return internal_server_error()
    else:
        return bad_request()    