# Contributing to Python Learning Platform

Thank you for considering contributing to this project! This document provides guidelines for contributing to the Python Learning Platform.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database:**
   - Install MySQL or configure SQLite for development
   - Update the `SQLALCHEMY_DATABASE_URI` in `app.py` if needed

5. **Run the application:**
   ```bash
   python app.py
   ```

## Testing

Run tests using pytest:

```bash
pytest
```

When adding new features, please include appropriate tests. The project uses pytest with fixtures defined in `tests/conftest.py`.

## Code Style Guidelines

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Include docstrings for modules, classes, and functions
- Keep functions short and focused on a single task

## Pull Request Process

1. Create a new branch for your feature or bugfix
2. Write tests for new functionality
3. Ensure all tests pass before submitting
4. Update documentation as needed
5. Submit a pull request with a clear description of the changes

## Reporting Issues

When reporting issues, please include:
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Error messages and stack traces if applicable
- Environment details (Python version, OS, etc.)

## Localization

The application supports multiple languages. When adding new text:
- Use the translation functions `_()` or `_l()`
- Add translations to the language files

## License

By contributing to this project, you agree that your contributions will be licensed under the project's license.
