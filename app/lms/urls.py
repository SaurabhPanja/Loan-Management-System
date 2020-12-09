from django.urls import path

from lms import views

app_name = 'lms'

urlpatterns = [
    path('users/', views.create_or_get_user, name='create_or_get_user'),
    path('login/', views.login, name='login'),
    path('user/<int:id>/change-status/', views.change_user_status, name='change_user_status'),
]