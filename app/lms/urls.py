from django.urls import path

from lms import views

app_name = 'lms'

urlpatterns = [
    path('users/', views.create_user, name='create_user'),
]