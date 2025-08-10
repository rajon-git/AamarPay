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

How to Run: 

    Local Setup: 
        1. Clone the repo.
        2. Create and activate a virtual environment.
        3. Install dependencies (pip install -r requirements.txt).
        4. In the root directory, create a .env file and edit it as shown 
        5. Run migrations (python manage.py migrate)
        6. Start Redis server (redis-server).
        7. Run Celery worker another terminal (celery -A aamarPay worker --loglevel=info).
        11. Start Django development server (python manage.py runserver).
        12. Visit http://localhost:8000/subscriptions to see the frontend subscription list.
        13. Done