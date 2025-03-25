# Videoflix Backend
A robust Django REST API for a video streaming platform featuring user authentication, video processing, and HLS streaming.

## Requirements
* Python must be installed.

## Getting Started
### Clone repositorys
* Clone this repository
* Clone the frontend repository [Videoflix Frontend](https://github.com/AntonOsipov99/videoflix_frontend)
### Installation
```bash
# Create a virtual environment in the project root and activate it

# On windows 
python -m venv env
env\Scripts\activate

# On Linux/Mac
python3 -m venv env
source env/bin/activate

# Install Dependencies
pip install -r requirements.txt

# Rename the .env.template to .env
- Open .env and enter your own configuration details

# Install PostgreSQL on Windows
- Visit the PostgreSQL Downloads page
- Run the installer and follow the setup wizard
psql -U postgres
CREATE DATABASE videoflix_db;

# Install PostgreSQL on Linux
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo -i -u postgres
psql
sudo -u postgres createdb your_db_name

# Run Migrations
python manage.py makemigrations
python manage.py migrate

# Starting Celery Worker
celery -A videoflix worker -l info

# Start development server
python manage.py runserver

# Your API should now be accessible at http://127.0.0.1:8000/

# Create superuser
python manage.py createsuperuser

# Login and create movies
- Go to http://127.0.0.1:8000/admin/ and log in.
- Create movies

# Testing
- Install test dependencies with
pip install pytest pytest-django pytest-cov

- Run tests with 
coverage report pytest --cov=videoflix_app --cov=user_auth_app

# Go to the frontend repository and follow the instructions from the readme