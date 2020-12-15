# Loan Management System

The application is built using Django and Django RestFramework. Postgresql is used to store data. The application provides API end-points. These endpoints can be used to perform different operations.  
The application does not use the built-in authentication and authorization system. The auth operations are performed with JWT authentication.  
Django and Django-Rest framework was chosen to build this application as it provides a good test suite.

## Start the application

```bash
sudo docker-compose up
```

## Test the application

```bash
sudo docker-compose run app sh -c "python manage.py test"
```

## User model
The user has three major entity email, password, and role. Password is not saved in the DB(obviously). It is salted and hashed. The hashed version is stored as a password hash, not the password directly.  
The role entity determines the role of a user, each role has different privileges, which is handled by the authorization system, code logic written in the controller for it.

## API routes

To create a user, make a POST request at this route

    '/api/users/'
    with payload {'emai':email, 'password' : password, 'role': role}
By default when a user other than a customer is created using this API route. The user is not active. An inactive user is as good as a non-existent user. It doesn't have any privileges. An admin has to activate the user so that the user can use the system.
Only admin can activate an agent.  
An agent cannot activate another agent.  
An admin can activate another admin.  
A customer is active by default. But can be changed by agent and admin user.

---
To view all users, make a GET request at this route.

    'api/users/'

An admin and agent can view all the users. A customer is not authorized to view this route, they are forbidden.  

---
To login, make a POST request at

    'api/login/' 
    with payload { 'email': email, 'password': password }
The login returns the JWT token. The token needs to send with every request to authenticate and sometimes authorize any operation.

---
To edit a user, make a POST request at

    'api/users/<id>/edit/'
    with payload {'email' : email, is_active: is_active }

An agent can only edit a customer.  
They cannot edit an agent user or an admin user.  
Admin can edit any user in the system.  
Customer is forbidden at this route.

---
To get a user, make a GET request at

    'api/users/<id>/'
A customer is only authorized to see themselves, whereas an agent can lookup any customer but not an agent user or admin user. An admin can lookup any user in the system.

---
To create a loan, make a POST request at

    'api/create-loan/'
    with payload customer-id, principal-amount, interest-rate, tenure-months
Only an agent can create a loan on behalf of a user. By default, the loan is in a 'new' state.

---
To approve a loan, make a POST request at

    'api/approve-loan/<loan_id>/'
Only the admin can approve a loan.

---
To edit a loan, make a POST request at
   
    'api/loan/<loan_id>/edit/
     with payload principal_amount, interest_rate, tenure_months, status
Only an agent can edit a loan. Reject a loan.
An agent cannot edit an approved loan.

---
To roll back to the previous history of a loan, make a POST request at

    'api/rollback-loan/<int:loan_id>/to/<int:edit_id>/
    where <loan_id> is the loan and <edit_id> is the id of the edited history.  
    Edit history is stored in the database every time an edit is made in the loan.
Rollback can only be performed by an agent.

---
To query a loan, make a GET request at

    'api/query-loan/
    with params created-date, update-date, loans-status

"customer" can only see their own loans...while "agent" and "admin" can see everyone's loans.

## License
[MIT](https://choosealicense.com/licenses/mit/)