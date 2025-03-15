from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit
import json
import os
import uuid
import nbformat
import subprocess
import sys
import io
import builtins

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
input_response = None
# URL of the GitHub repository
REPO_URL = 'https://github.com/msy-bilecik/ist204_2025'


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


@app.route('/refresh_repo')
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
def run_code():
    """Store code temporarily and return an ID to reference it"""
    code = request.json.get('code', '')
    code_id = str(uuid.uuid4())

    # Store code in session or temporary storage
    app.config.setdefault('CODE_STORAGE', {})[code_id] = code

    return jsonify({'code_id': code_id})




@app.route('/console/<code_id>')
def python_console(code_id):
    """Show Python console with the specified code"""
    code = app.config.get('CODE_STORAGE', {}).get(code_id, '')
    return render_template('console.html', code=code)


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
    # Clone repo first
    clone_repo()
    socketio.run(app, debug=True, port=5000)