from django.http import JsonResponse
from lms.models import User
from rest_framework import status

#users api
def create_user(request):
    error = False
    if request.method == "POST":
        try:
            request_data = request.POST
            new_user = User()
            new_user.email = request_data['email']
            new_user.save_password_hash(request_data['password'])
            new_user.role = 'customer'
            if request_data['role'] == 'customer':
                new_user.is_active = True    
            new_user.save()

        except:
            error = True
        
        if error:
            response = {
                'message' : 'Internal server error.',
                'status' : status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return JsonResponse(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            response = {
                'message' : 'New user created',
                'status' : status.HTTP_201_CREATED
            }

            return JsonResponse(response, status=status.HTTP_201_CREATED)
    else:
        pass

