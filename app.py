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
import builtins
from datetime import datetime
from flask_babel import Babel, gettext as _, lazy_gettext as _l
from functools import wraps
from flask import abort

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://radome:12345@localhost/python_platform'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initialize Babel
babel = Babel(app)

# Configure supported languages
app.config['BABEL_DEFAULT_LOCALE'] = 'tr'  # Default language (Turkish)
app.config['BABEL_SUPPORTED_LOCALES'] = ['tr', 'en']  # Supported languages

# Initialize extensions
db = SQLAlchemy(app)
socketio = SocketIO(app, async_mode='threading')
login_manager = LoginManager(app)
login_manager.login_view = 'login'

input_response = None

# New approach using init app
def get_locale():
    if 'language' in session:
        return session['language']
    return request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'])

babel.init_app(app, locale_selector=get_locale)

@app.route('/language/<lang>')
def set_language(lang):
    if lang in app.config['BABEL_SUPPORTED_LOCALES']:
        session['language'] = lang
    return redirect(request.referrer or url_for('index'))

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

    return render_template('edit_roles.html', user=user, roles=roles)

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
    users = User.query.all()
    return render_template('admin.html', users=users)

# Modify existing routes to check permissions
@app.route('/refresh_repo')
@login_required
@role_required('teacher')  # Only teachers can refresh the repository
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
    notebook_path = os.path.join(repo_dir, path)

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
        return f"Error loading notebook: {str(e)}", 500


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
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
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

@socketio.on('run_code')
def handle_run_code(data):
    code = data['code']

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
    builtins.input = custom_input

    try:
        # Execute the code
        exec(code)
        # Send any remaining output
        final_output = redirected_output.getvalue()[last_output_position:]
        if final_output:
            emit('partial_output', {'output': final_output})
    except Exception as e:
        emit('partial_output', {'output': str(e)})
    finally:
        # Restore the original functions
        sys.stdout = old_stdout
        builtins.input = old_input

    emit('code_output', {'output': ''})  # Signal completion

# Add this new event handler
@socketio.on('input_response')
def handle_input_response(data):
    global input_response
    input_response = data['value']


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