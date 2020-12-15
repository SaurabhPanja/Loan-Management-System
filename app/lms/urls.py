from django.urls import path

from lms import views

app_name = 'lms'

urlpatterns = [
    path('users/', views.create_or_get_user, name='create_or_get_user'),
    path('login/', views.login, name='login'),
    path('user/<int:id>/edit/', views.edit_user, name='edit_user'),
    path('user/<int:id>/', views.get_user, name='get_user'),
    path('create-loan/', views.create_loan, name='create_loan'),
    path('approve-loan/<int:id>/', views.approve_loan, name='approve_loan'),
    path('loan/<int:id>/edit/', views.edit_loan, name="edit_loan"),
    path('rollback-loan/<int:loan_id>/to/<int:edit_id>/',views.rollback_loan, name="rollback_loan"),
    path('query-loan/', views.query_loan, name="query_loan"),
]