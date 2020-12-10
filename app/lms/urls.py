from django.urls import path

from lms import views

app_name = 'lms'

urlpatterns = [
    path('users/', views.create_or_get_user, name='create_or_get_user'),
    path('login/', views.login, name='login'),
    path('user/<int:id>/edit/', views.edit_user, name='edit_user'),
    path('user/<int:id>/', views.get_user, name='get_user'),
    path('create-loan/', views.create_loan, name='create_loan'),
]