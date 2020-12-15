from django.http import JsonResponse
from rest_framework import status
import jwt
from app.settings import SECRET_KEY
import sys
import re

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
        encoded = encoded.split(' ')[-1] if encoded else ''
        decoded = jwt.decode(encoded, SECRET_KEY, algorithms=['HS256'])
        email = decoded['email']
        role = decoded['role']   

        return email, role 

def authorize_user(func):
    def wrap(request, *args, **kwargs):
        encoded = request.META.get('HTTP_AUTHORIZATION', '')
        encoded = encoded.split(' ')[-1] if encoded else ''
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

