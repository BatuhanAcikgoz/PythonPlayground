# PythonPlayground Project Guidelines

## Project Overview
PythonPlayground is an interactive Python console and education platform that allows users to view and run Jupyter notebooks stored in a GitHub repository. The application provides a Programiz-like interactive console and includes user management with role-based access control.

### Key Features
- **User Management**: Comprehensive registration, login, and role assignment system
- **Role-Based Access**: Student, teacher, and admin permission levels
- **Multilingual Support**: Turkish and English interface
- **Notebook Integration**: Automatic fetching and updating of Jupyter notebooks from GitHub
- **Interactive Console**: Real-time code execution and output display
- **Admin Panel**: Centralized management of users and roles
- **Responsive Design**: Mobile-friendly interface
- **Progress Tracking**: Monitoring of users' educational progress
- **Gamification**: Badges and leaderboard for learning motivation

## Project Structure
The project follows a modular structure:
```
project_root/
  ├── app/                  # Main application package
  │   ├── __init__.py       # Flask app initialization
  │   ├── models/           # Database models
  │   ├── forms/            # Form definitions
  │   ├── routes/           # Flask views/routes
  │   ├── services/         # Business logic services
  │   ├── static/           # CSS, JS, images
  │   ├── templates/        # Jinja2 templates
  │   └── utils/            # Helper functions
  ├── app.py                # Main Flask application
  ├── api.py                # FastAPI application
  ├── config.py             # Configuration settings
  ├── tests/                # Test directory
  │   ├── conftest.py       # Pytest fixtures
  │   ├── mock_app.py       # Mock app for testing
  │   └── test_*.py         # Test files
  ├── notebooks_repo/       # Repository for Jupyter notebooks
  └── requirements.txt      # Dependencies
```

## Technology Stack
- **Backend**: Python 3.8+, Flask 3.1.0, FastAPI 0.110.0
- **Database**: MySQL 5.7+ or MariaDB 10.5+
- **ORM**: SQLAlchemy 2.0.0+
- **Frontend**: HTML, CSS, JavaScript, Jinja2 templates
- **API**: RESTful API with FastAPI, Swagger documentation
- **Testing**: pytest

## Development Guidelines

### Setup and Installation
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up the MySQL database
6. Configure the application in `config.py`
7. Initialize the database: `python app.py`

### Running the Application
- Flask application: `python app.py`
- FastAPI application runs automatically in a separate thread

### Testing Requirements
Junie should run tests to verify the correctness of any proposed solution. The project uses pytest for testing.

To run tests:
```bash
pytest
```

For specific test files:
```bash
pytest tests/test_api.py
pytest tests/test_auth.py
```

For test coverage:
```bash
pytest --cov=app tests/
```

### Code Style Guidelines
- Follow PEP 8 style guidelines for Python code
- Use docstrings for all functions, classes, and modules
- Maintain consistent indentation (4 spaces)
- Use meaningful variable and function names
- Keep functions and methods focused on a single responsibility
- Write comprehensive tests for new functionality
- Include type hints where appropriate

### Pull Request Process
1. Create a feature branch from the main branch
2. Make your changes
3. Run tests to ensure they pass
4. Submit a pull request with a clear description of the changes

## API Documentation
The API documentation is available at `http://localhost:8000/docs` when the application is running. This provides a Swagger UI for interacting with the API endpoints.

## Deployment
For production deployment:
1. Set a secure SECRET_KEY
2. Turn off debug mode
3. Use HTTPS
4. Run behind Gunicorn or uWSGI
5. Use a reverse proxy like Nginx or Apache

## Additional Resources
- [Flask Documentation](https://flask.palletsprojects.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pytest Documentation](https://docs.pytest.org/)