Project Title: Payment Gateway Integration and Files Uploading System

All API endpoints Postman documentation below: https://documenter.getpostman.com/view/24667147/2sB3BEnVHF

Features:
    1. User registration, login, logout (DRF Auth)
    2. aamarPay sandbox payment integration
    3. Payment status tracking
    4. File uploads (only after payment)
    5. Admin dashboard with restricted staff access
    6. Activity logs
    7. Celery + Redis for background tasks

Description of the Payment Flow Implementation:
    1. InitiatePaymentView (POST /api/initiate-payment/)
        i. Starts a payment by sending user and payment info to aamarPay sandbox.
        ii. It collects user details and a fixed payment amount (৳100), then sends this data to the aamarPay sandbox payment gateway via a POST request.
        iii. Upon success, it creates a PaymentTransaction record with status "initiated" and logs this event.
        iv. The view then returns a payment redirect URL to send the user to complete the payment.
    2. PaymentSuccessView
        i. This API receives a callback from aamarPay after payment completion. 
        ii.  It retrieves the corresponding PaymentTransaction by transaction ID and updates its status to "success" or "failed" based on the payment result sent by aamarPay.
        iii. t also saves the payment gateway’s response data, logs the success or failure activity, and returns confirmation of the recorded payment status.

How To Run: 

    Initially I setup for Localhost.

    Local Host Setup: 
        1. Clone the repo.
        2. Create and activate a virtual environment.
        3. Install dependencies (pip install -r requirements.txt).
        4. If you can use SQLite:
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': BASE_DIR / 'db.sqlite3',
                }
            }

            If want use MySQL:
            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.mysql',
                    'NAME': config("MYSQL_DATABASE"),
                    'USER': config("MYSQL_USER"),
                    'PASSWORD': config("MYSQL_PASSWORD"),
                    'HOST': 'localhost',
                    'PORT': '3306',
                }
            }
        5. In the root directory, create a .env file and edit it as shown 
        6. Run migrations (python manage.py migrate)
        7. Start Redis server (redis-server).
        8. Run Celery worker another terminal (celery -A aamarPay worker --loglevel=info).
        9. Start Django development server (python manage.py runserver).
        10. Visit http://localhost:8000/dashboard/ to see the frontend Dashboard.
        11. Done

    Docker usage Setup:
        1. Create .env File.
        2. When Docker is used, the settings.py file must include: 
            CELERY_BROKER_URL = "redis://redis:6379/0"
            CELERY_RESULT_BACKEND = 'redis://redis:6379/0'DatabaseScheduler'

            and in Database use 'HOST': 'db',

            DATABASES = {
                'default': {
                    'ENGINE': 'django.db.backends.mysql',
                    'NAME': config("MYSQL_DATABASE"),
                    'USER': config("MYSQL_USER"),
                    'PASSWORD': config("MYSQL_PASSWORD"),
                    'HOST': 'db',
                    'PORT': '3306',
                }
            }

        3. sudo docker ps -a (from there get container ID).
        4. sudo docker start .... (there give aamarpay-web container ID).
        5. sudo docker start .... (there give aamarpay-celery container ID).
        6. sudo docker start .... (there give mysql:8.0 container ID).
        7. sudo docker ps (Check there redis:alpine this container running. 
            or not, if running then next command else start this with container ID or name).
        8. sudo docker-compose run web bash / sudo docker exec -it (there give aamarpay-web container ID) bash.
        9. Create an superuser 
        10. Done