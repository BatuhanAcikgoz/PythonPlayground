from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
import uuid
import nbformat
import subprocess
import sys
import io
from urllib.parse import urlparse
import builtins
from datetime import datetime
from flask_babel import Babel, gettext as _, lazy_gettext as _l
from functools import wraps
from flask import abort
from werkzeug.utils import secure_filename
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
logging.basicConfig(level=logging.ERROR)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://radome:12345@localhost/python_platform'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initialize Babel
# Configure supported languages
app.config['BABEL_DEFAULT_LOCALE'] = 'tr'  # Default language (Turkish)
app.config['BABEL_SUPPORTED_LOCALES'] = ['tr', 'en']  # Supported languages
# Near the top of app.py, with other configurations
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # Session lifetime in seconds
babel = Babel(app)

# Initialize extensions
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

input_response = None

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Add relationship to questions
    questions = db.relationship('Question', backref='course', lazy=True)

    def __repr__(self):
        return f'<Course {self.name}>'

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    # Foreign key relationship with Course
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    def __repr__(self):
        return f'<Question {self.title}>'

# New approach using init app
def get_locale():
    # First check if user has explicitly set a language in session
    if 'language' in session:
        return session['language']
    # Always default to 'tr' rather than using browser preferences
    return app.config['BABEL_DEFAULT_LOCALE']

babel.init_app(app, locale_selector=get_locale)

@app.route('/language/<lang>')
def set_language(lang):
    if lang in app.config['BABEL_SUPPORTED_LOCALES']:
        session.permanent = True  # Make session permanent
        session['language'] = lang
    referrer = request.referrer or url_for('index')
    referrer = referrer.replace('\\', '')
    if not urlparse(referrer).netloc and not urlparse(referrer).scheme:
        return redirect(referrer, code=302)
    return redirect(url_for('index'), code=302)

# Role model definitions
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f'<Role {self.name}>'


# User-role association table for many-to-many relationship
user_roles = db.Table('user_roles',
                      db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                      db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
                      )


# Update User model with role relationship
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Add roles relationship
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Add permission check methods
    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)

    def is_admin(self):
        return self.has_role('admin')

    def is_teacher(self):
        return self.has_role('teacher') or self.is_admin()

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# URL of the GitHub repository
REPO_URL = 'https://github.com/msy-bilecik/ist204_2025'

@app.route('/js/component/<filename>')
def serve_component(filename):
    base_path = os.path.join(app.template_folder, 'js', 'components')
    safe_filename = secure_filename(filename)
    file_path = os.path.normpath(os.path.join(base_path, safe_filename))
    if not file_path.startswith(base_path):
        abort(403)
    with open(file_path, 'r') as file:
        content = file.read()
    return content, 200, {'Content-Type': 'text/javascript'}

def role_required(role_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login', next=request.url))
            if not current_user.has_role(role_name):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def init_roles():
    """Initialize default roles if they don't exist"""
    roles = {
        'student': 'Basic access to view notebooks',
        'teacher': 'Can manage notebooks and view student progress',
        'admin': 'Full administrative access'
    }

    for role_name, description in roles.items():
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name, description=description)
            db.session.add(role)

    db.session.commit()

@app.route('/admin/user/<int:user_id>/roles', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_user_roles(user_id):
    user = User.query.get_or_404(user_id)
    roles = Role.query.all()

    if request.method == 'POST':
        # Clear existing roles
        user.roles = []

        # Add selected roles
        role_ids = request.form.getlist('roles')
        for role_id in role_ids:
            role = Role.query.get(role_id)
            if role:
                user.roles.append(role)

        db.session.commit()
        flash(_('user_roles_updated'))
        return redirect(url_for('admin_panel'))

    return render_template('admin/edit_roles.html', user=user, roles=roles)

@app.route('/admin/user/<int:user_id>/delete')
@login_required
@role_required('admin')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.username == 'admin':
        flash(_('admin_cannot_delete'), 'error')
    else:
        username = user.username
        db.session.delete(user)
        db.session.commit()
        flash(_('user_deleted_success'), 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/user/new', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def new_user():
    roles = Role.query.all()

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        user = User(username=username, email=email)
        user.set_password(password)

        # Add selected roles
        role_ids = request.form.getlist('roles')
        for role_id in role_ids:
            role = Role.query.get(role_id)
            if role:
                user.roles.append(role)

        db.session.add(user)
        db.session.commit()
        flash(_('user_created'))
        return redirect(url_for('admin_panel'))

    return render_template('new_user.html', roles=roles)

def clone_repo():
    """Clone or update the repository"""
    repo_dir = os.path.join(os.getcwd(), 'notebooks_repo')

    if os.path.exists(repo_dir):
        print(f"Updating repository in {repo_dir}")
        try:
            # Pull latest changes
            subprocess.run(['git', 'pull'], cwd=repo_dir, check=True)
            return repo_dir
        except subprocess.CalledProcessError:
            print("Error updating repository, attempting to clone fresh")
            # If pull fails, try cloning fresh
            import shutil
            shutil.rmtree(repo_dir, ignore_errors=True)

    print(f"Cloning repository to {repo_dir}")
    try:
        subprocess.run(['git', 'clone', REPO_URL, repo_dir], check=True)
        return repo_dir
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e}")
        return None

# Example of using the decorator for admin-only routes
@app.route('/admin')
@login_required
@role_required('admin')
def admin_panel():
    all_users = User.query.all()
    users_data = []

    for user in all_users:
        user_dict = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'roles': [{'id': role.id, 'name': role.name} for role in user.roles]
        }
        users_data.append(user_dict)

    return render_template('admin/admin.html', users=users_data)

# Modify existing routes to check permissions
@app.route('/refresh_repo')
@login_required
@role_required('admin')  # Only teachers can refresh the repository
def refresh_repo():
    """Refresh the repository by pulling the latest changes"""
    clone_repo()
    return redirect(url_for('index'))

@app.route('/')
def index():
    # List of notebook files in the repository
    repo_dir = os.path.join(os.getcwd(), 'notebooks_repo')
    notebooks = []
    error_message = None

    # Check if repo directory exists
    if os.path.exists(repo_dir):
        # List all ipynb files
        for root, dirs, files in os.walk(repo_dir):
            for file in files:
                if file.endswith('.ipynb'):
                    rel_path = os.path.relpath(os.path.join(root, file), repo_dir)
                    notebooks.append(rel_path)

        if not notebooks:
            error_message = "No .ipynb files found in the repository."
    else:
        error_message = "Repository not yet cloned."

    return render_template('index.html', notebooks=notebooks, error_message=error_message)

@app.route('/view/<path:path>')
@login_required
def view_notebook(path):
    """Display notebook as HTML with run buttons"""
    repo_dir = os.path.join(os.getcwd(), 'notebooks_repo')
    notebook_path = os.path.normpath(os.path.join(repo_dir, path))

    if not notebook_path.startswith(repo_dir):
        return "Invalid notebook path", 400

    if not os.path.exists(notebook_path):
        return "Notebook not found", 404

    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook_content = json.load(f)

        # Use nbformat to validate and read the notebook
        notebook = nbformat.reads(json.dumps(notebook_content), as_version=4)

        return render_template('notebook_viewer.html',
                               notebook=notebook,
                               notebook_path=path)
    except Exception as e:
        logging.error(f"Error loading notebook: {str(e)}")
        return "An internal error has occurred while loading the notebook.", 500


@app.route('/run_code', methods=['POST'])
@login_required
def run_code():
    """Store code temporarily and return an ID to reference it"""
    code = request.json.get('code', '')
    code_id = str(uuid.uuid4())

    # Store the user ID with the code
    app.config.setdefault('CODE_STORAGE', {})[code_id] = {
        'code': code,
        'user_id': current_user.id
    }

    return jsonify({'code_id': code_id})


# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next', '')
            next_page = next_page.replace('\\', '')
            if not urlparse(next_page).netloc and not urlparse(next_page).scheme:
                return redirect(next_page or url_for('index'))
            return redirect(url_for('index'))
        else:
            flash(_('invalid_login'))

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if username or email already exists
        user_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()

        if user_exists:
            flash(_('username_exists'))
        elif email_exists:
            flash(_('email_exists'))
        else:
            user = User(username=username, email=email)
            user.set_password(password)

            # Assign default student role
            student_role = Role.query.filter_by(name='student').first()
            if student_role:
                user.roles.append(student_role)

            db.session.add(user)
            db.session.commit()

            login_user(user)
            return redirect(url_for('index'))

    return render_template('register.html')

@app.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403

@app.errorhandler(404)
def forbidden(error):
    return render_template('404.html'), 404

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.context_processor
def utility_processor():
    def now():
        return datetime.utcnow()
    return dict(now=now)


# Add this near other global variables
user_namespaces = {}  # Dictionary to store execution environments for each user


@socketio.on('run_code')
def handle_run_code(data):
    code = data['code']
    user_id = current_user.id

    # Get or create namespace for this user
    if user_id not in user_namespaces:
        user_namespaces[user_id] = {'__builtins__': __builtins__}

    user_namespace = user_namespaces[user_id]

    # Create a StringIO object to capture stdout
    old_stdout = sys.stdout
    redirected_output = io.StringIO()
    sys.stdout = redirected_output

    # Track what has been sent already
    last_output_position = 0

    # Custom input function that uses Socket.IO
    def custom_input(prompt=''):
        global input_response

        # Send any pending output before requesting input
        nonlocal last_output_position
        current_output = redirected_output.getvalue()[last_output_position:]
        if current_output:
            emit('partial_output', {'output': current_output})
            last_output_position = len(redirected_output.getvalue())

        # Now request input
        input_response = None
        emit('input_request', {'prompt': prompt})

        # Wait for input_response to be set
        while input_response is None:
            socketio.sleep(0.1)

        response = input_response
        input_response = None
        return response

    old_input = builtins.input
    user_namespace['input'] = custom_input

    try:
        # Check if the code is a simple expression (single line that could return a value)
        is_simple_expression = False
        try:
            compiled_code = compile(code, '<string>', 'eval')
            is_simple_expression = True
        except SyntaxError:
            pass

        if is_simple_expression:
            # Simple expression - evaluate and show result
            result = eval(compiled_code, user_namespace)
            if result is not None:
                print(repr(result))
        else:
            # For multi-line code, use ast to check if the last statement is an expression
            import ast

            try:
                # Parse the code into an AST
                parsed = ast.parse(code)

                # Check if there's at least one statement
                if parsed.body:
                    last_stmt = parsed.body[-1]

                    # Check if the last statement is an expression
                    if isinstance(last_stmt, ast.Expr):
                        # Split the code into all statements except the last, and the last statement
                        lines = code.splitlines()
                        last_line_index = last_stmt.lineno - 1  # ast line numbers are 1-indexed

                        # If it's the only line, execute normally with exec
                        if len(lines) == 1:
                            exec(code, user_namespace)
                        else:
                            # Execute all except last expression
                            exec('\n'.join(lines[:last_line_index]), user_namespace)

                            # Evaluate the last expression and print its result
                            last_expr = lines[last_line_index]
                            result = eval(last_expr, user_namespace)
                            if result is not None:
                                print(repr(result))
                    else:
                        # Not an expression, execute normally
                        exec(code, user_namespace)
                else:
                    # Empty code
                    exec(code, user_namespace)
            except SyntaxError:
                # If AST parsing fails, execute normally
                exec(code, user_namespace)

        # Send any remaining output
        final_output = redirected_output.getvalue()[last_output_position:]
        if final_output:
            emit('partial_output', {'output': final_output})
    except Exception as e:
        emit('partial_output', {'output': str(e)})
    finally:
        # Restore the original stdout
        sys.stdout = old_stdout
        builtins.input = old_input

    emit('code_output', {'output': ''})  # Signal completion

@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        user_id = current_user.id
        # Clear the user's namespace if it exists
        if user_id in user_namespaces:
            user_namespaces[user_id] = {'__builtins__': __builtins__}
            print(f"Reset namespace for user {user_id}")

# Add this new event handler
@socketio.on('input_response')
def handle_input_response(data):
    global input_response
    input_response = data['value']

@app.route('/api/server-status')
@login_required
@role_required('admin')
def server_status():
    import platform
    import psutil
    import flask
    from sqlalchemy import text  # Import text function

    # Get Python version
    python_version = platform.python_version()

    # Get Flask version
    flask_version = flask.__version__

    # Get MySQL version
    try:
        mysql_version_query = text("SELECT VERSION() as version")  # Wrap with text()
        mysql_result = db.session.execute(mysql_version_query).first()
        mysql_version = mysql_result.version if mysql_result else "Unknown"
    except Exception as e:
        app.logger.error(f"Error fetching MySQL version: {str(e)}")
        mysql_version = "Error: Unable to fetch MySQL version"

    # Get system RAM usage
    mem = psutil.virtual_memory()
    ram_used = round(mem.used / (1024 * 1024 * 1024), 2)  # GB
    ram_total = round(mem.total / (1024 * 1024 * 1024), 2)  # GB

    # Get process-specific RAM usage
    process = psutil.Process(os.getpid())
    process_memory = process.memory_info()
    process_ram_used = round(process_memory.rss / (1024 * 1024 * 1024), 2)  # GB - Resident Set Size
    process_ram_allocated = round(process_memory.vms / (1024 * 1024 * 1024), 2)  # GB - Virtual Memory Size

    # Get CPU usage
    cpu_usage = psutil.cpu_percent(interval=1)

    return jsonify({
        'python_version': python_version,
        'flask_version': flask_version,
        'mysql_version': mysql_version,
        'ram_used': ram_used,
        'ram_total': ram_total,
        'cpu_usage': cpu_usage,
        'process_ram_used': process_ram_used,
        'process_ram_allocated': process_ram_allocated
    })


@app.route('/api/recent-questions')
@login_required
@role_required('admin')
def recent_questions():
    # Assuming you have a Question model
    # Fetch the 10 most recent questions
    recent = db.session.query(
        Question,
        Course.name.label('course_name')
    ).join(
        Course,
        Question.course_id == Course.id
    ).order_by(
        Question.created_at.desc()
    ).limit(10).all()

    questions = []
    for q, course_name in recent:
        questions.append({
            'id': q.id,
            'title': q.title,
            'course_name': course_name,
            'created_at': q.created_at.isoformat() if q.created_at else None
        })

    return jsonify({'questions': questions})


@app.route('/api/recent-users')
@login_required
@role_required('admin')
def recent_users():
    # Fetch the 5 most recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

    users_data = []
    for user in recent_users:
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'roles': [{'id': role.id, 'name': role.name} for role in user.roles]
        }
        users_data.append(user_data)

    return jsonify({'users': users_data})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
        init_roles()  # Initialize default roles

        # Create an admin user if none exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@example.com')
            admin.set_password('admin123')  # Change this to a secure password in production
            admin_role = Role.query.filter_by(name='admin').first()
            admin.roles.append(admin_role)
            db.session.add(admin)
            db.session.commit()

    # Start the Flask server
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)