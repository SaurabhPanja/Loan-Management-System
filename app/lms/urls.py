from django.urls import path

from lms import views

app_name = 'lms'

urlpatterns = [
    path('users/', views.create_or_get_user, name='create_or_get_user'),
    path('login/', views.login, name='login'),
]