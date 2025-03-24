# Videoflix
A robust Django REST API for a video streaming platform featuring user authentication, video processing, and HLS streaming.
## Installation
* Clone the repository with "git clone git@github.com:AntonOsipov99/videoflix_backend.git".
* Then go to the directory with "cd videoflix_backend" in VS Code.
* Create a Virtual Environment with "python -m venv env".
* Start the environment with "env\Scripts\activate" on windows or with "source env/bin/activate" on macOS/Linux.
* Then install the requirements.txt with "pip install -r requirements.txt".
* Create a .env in the project root:
"DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
Django settings
SECRET_KEY=your_secret_key_here
DEBUG=True
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yourprovider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USER=your_email@example.com
EMAIL_PASSWORD=your_email_password
DEFAULT_FROM_EMAIL=your_email@example.com
FRONTEND_URL=http://localhost:4200".
* Create the PostgreSQL database with "createdb your_db_name".
* Run migrations with "python manage.py migrate".
* Start Redis server with "redis-server".
* Start the Celery worker for background tasks with "celery -A videoflix worker -l info".
* Run the Development Server with "python manage.py runserver".
* Your API should now be accessible at http://127.0.0.1:8000/.
* Install test dependencies with "pip install pytest pytest-django pytest-cov".
* Run tests with "coverage report pytest --cov=videoflix_app --cov=user_auth_app".
