from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
import requests
from typing import Optional, Dict, Any
import json
import os
from models import db, User
from forms import LoginForm, RegistrationForm, ProfileForm
import click

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-please-change')  # Change in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
csrf = CSRFProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# CLI commands
@app.cli.command("init-db")
def init_db():
    """Initialize the database."""
    click.echo('Creating database tables...')
    db.create_all()
    click.echo('Database tables created successfully!')

# Create the database tables within an application context
with app.app_context():
    db.create_all()

class TerraformModuleClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')

    def search_modules(
        self,
        query: str = "",
        provider: Optional[str] = None,
        namespace: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        params = {k: v for k, v in locals().items() if v is not None and k not in ['self', 'headers']}
        response = requests.get(f"{self.base_url}/v1/modules/search", params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_module_versions(self, namespace: str, name: str, provider: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/v1/modules/{namespace}/{name}/{provider}/versions",
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    def get_module_details(self, namespace: str, name: str, provider: str, version: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/v1/modules/{namespace}/{name}/{provider}/{version}",
            headers=headers
        )
        response.raise_for_status()
        return response.json()

# Initialize the client
client = TerraformModuleClient()

# Default values in case the backend is not accessible
DEFAULT_NAMESPACES = ["hashicorp", "terraform-aws-modules", "terraform-google-modules"]
DEFAULT_PROVIDERS = ["aws", "azure", "gcp", "kubernetes"]

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html', form=form)
        
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        user.permissions = ['read:module']  # Default permission
        user.namespaces = []  # Empty namespace list by default
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        if form.current_password.data and not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return render_template('profile.html', form=form)
        
        if form.email.data != current_user.email:
            if User.query.filter_by(email=form.email.data).first():
                flash('Email already registered.', 'danger')
                return render_template('profile.html', form=form)
            current_user.email = form.email.data
        
        if form.new_password.data:
            current_user.set_password(form.new_password.data)
        
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile'))
    
    elif request.method == 'GET':
        form.email.data = current_user.email
    
    return render_template('profile.html', form=form)

@app.route('/generate_token', methods=['POST'])
@login_required
def generate_token():
    # Generate token using backend service
    try:
        # Make request to backend to generate token
        response = requests.post(
            f"{client.base_url}/auth/token",
            json={
                "user_id": current_user.id,
                "email": current_user.email,
                "permissions": current_user.permissions
            }
        )
        response.raise_for_status()
        token_data = response.json()
        
        # Update user's token
        current_user.token = token_data.get('token')
        db.session.commit()
        
        flash('API token generated successfully.', 'success')
    except Exception as e:
        flash(f'Error generating token: {str(e)}', 'danger')
    
    return redirect(url_for('profile'))

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('index.html', 
                         namespaces=current_user.namespaces or DEFAULT_NAMESPACES,
                         providers=DEFAULT_PROVIDERS)

@app.route('/api/search')
@login_required
def search_modules():
    try:
        query = request.args.get('query', '')
        provider = request.args.get('provider')
        namespace = request.args.get('namespace')
        
        # Add token to request if available
        headers = {}
        if current_user.token:
            headers['Authorization'] = f'Bearer {current_user.token}'
        
        results = client.search_modules(
            query=query,
            provider=provider if provider else None,
            namespace=namespace if namespace else None,
            headers=headers
        )
        return jsonify(results)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/modules/<namespace>/<name>/<provider>/versions')
@login_required
def get_versions(namespace, name, provider):
    try:
        headers = {}
        if current_user.token:
            headers['Authorization'] = f'Bearer {current_user.token}'
            
        versions = client.get_module_versions(
            namespace=namespace,
            name=name,
            provider=provider,
            headers=headers
        )
        return jsonify(versions)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/modules/<namespace>/<name>/<provider>/<version>')
@login_required
def get_module_details(namespace, name, provider, version):
    try:
        headers = {}
        if current_user.token:
            headers['Authorization'] = f'Bearer {current_user.token}'
            
        details = client.get_module_details(
            namespace=namespace,
            name=name,
            provider=provider,
            version=version,
            headers=headers
        )
        return jsonify(details)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)