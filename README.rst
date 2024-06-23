Create a superuser if you haven't already:
python manage.py createsuperuser

Run the server:
python manage.py runserver

Go to the Django admin interface at http://localhost:8000/admin/ and log in with your superuser account.
Navigate to OAuth2 Provider > Applications and add a new application:

    Name: Your application name (e.g., MyApp)
    Client ID: This will be generated automatically.
    Client Secret: This will be generated automatically.
    Client Type: Confidential
    Authorization Grant Type: Resource owner password-based