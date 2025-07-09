# Django Todo List Application - Agent Configuration

## Build/Lint/Test Commands
- `python manage.py runserver` - Start development server
- `python manage.py migrate` - Run database migrations  
- `python manage.py makemigrations` - Create new migrations
- `python manage.py test` - Run all tests
- `python manage.py test todoapp.tests.TestTodoModel` - Run specific test
- `python manage.py collectstatic` - Collect static files
- `python manage.py createsuperuser` - Create admin user
- `./build.sh` - Production build script

## Architecture & Structure
- Django 5.0.2 application with SQLite (dev) and PostgreSQL (production)
- Main app: `todoapp/` - Core todo functionality with models, views, URLs
- Project settings: `todoproject/` - Django project configuration
- Database: SQLite (`db.sqlite3`) for development
- Templates in `templates/` directory
- Uses Django REST Framework for API endpoints
- Real-time features via Django Channels
- Authentication via django-allauth

## Code Style & Conventions
- Follow Django conventions: PascalCase for models, snake_case for functions/variables
- Import order: Django imports first, then third-party, then local
- Models use `models.Model` base class with proper field types and validators
- Views use class-based views where appropriate
- URL patterns in separate `urls.py` files
- Use Django's built-in authentication system
- Environment variables for sensitive settings (SECRET_KEY, DEBUG)
- Bootstrap 4 with crispy-forms for frontend styling
