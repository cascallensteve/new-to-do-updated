# Django Todo List Application

A feature-rich todo list application built with Django, featuring user authentication, task management, and a modern UI.

## Features

- User authentication (login, register, password reset)
- Create, read, update, and delete tasks
- Task categories and tags
- Task priority levels
- Progress tracking
- Modern, responsive UI with Bootstrap 5

## Tech Stack

- Django 5.0.2
- Python 3.13
- Bootstrap 5
- SQLite (development)
- django-allauth for authentication
- django-crispy-forms for form styling
- Additional packages: colorfield, taggit, ckeditor

## Deployment

This application is configured for deployment on Render.com.

### Deployment Steps on Render:

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Use the following settings:
   - Build Command: `./build.sh`
   - Start Command: `gunicorn todoproject.wsgi:application`
4. Add the following environment variables:
   - `DJANGO_SECRET_KEY`: Your secret key
   - `DJANGO_DEBUG`: False
   - `PYTHON_VERSION`: 3.13.2

## Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/cascallensteve/to-do-list.git
   cd to-do-list
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

## License

MIT License 