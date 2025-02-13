from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, current_app, Response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_migrate import Migrate
from flask_cors import CORS
from urllib.parse import urlparse
from typing import Dict, Any, Optional
import requests
import re
import os
import logging
import sys
from models import db, User, Repository
from forms import LoginForm, RegistrationForm, ProfileForm, RepositoryForm, AdminUserForm
from dotenv import load_dotenv
from werkzeug.exceptions import HTTPException

# Set up logging to stdout
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Load environment variables first
load_dotenv()
logger.info("Environment variables loaded")

app = Flask(__name__)
CORS(app)  # Enable CORS
logger.info("Flask app created with CORS enabled")

# Database Configuration with error handling
try:
    # Build PostgreSQL URL from environment variables
    db_url = f"postgresql://{os.environ.get('DB_USER', 'admin')}:{os.environ.get('DB_PASSWORD', 'adminpass')}@{os.environ.get('DB_HOST', 'postgres')}:{os.environ.get('DB_PORT', '5432')}/{os.environ.get('DB_NAME', 'moduledb')}"
    
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-please-change'),
        SQLALCHEMY_DATABASE_URI=db_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_ENABLED=True,
        WTF_CSRF_SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-please-change'),
        BACKEND_URL=os.environ.get('BACKEND_URL', 'http://localhost:8000')  # Changed default to 8000
    )
    logger.info(f"App configuration loaded with backend URL: {app.config['BACKEND_URL']}")
except Exception as e:
    logger.error(f"Error configuring application: {e}")
    sys.exit(1)

# Initialize extensions with error handling
try:
    db.init_app(app)
    logger.info("Database initialized")
    
    migrate = Migrate(app, db)
    logger.info("Migration system initialized")
    
    csrf = CSRFProtect(app)
    logger.info("CSRF protection initialized")
    
    login_manager = LoginManager(app)
    login_manager.login_view = 'login'
    logger.info("Login manager initialized")
except Exception as e:
    logger.error(f"Error initializing extensions: {e}")
    sys.exit(1)

# Attempt database connection and table creation
def init_db():
    try:
        with app.app_context():
            db.create_all()
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        return False
    return True

# Default values
DEFAULT_NAMESPACES = ["hashicorp", "terraform-aws-modules", "terraform-google-modules"]
DEFAULT_PROVIDERS = ["aws", "azure", "gcp", "kubernetes"]

class TerraformModuleClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.token = None

    def set_jwt_token(self, token: str):
        self.token = token

    def get_headers(self) -> Dict[str, str]:
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers

    def search_modules(
        self,
        query: str = "",
        provider: Optional[str] = None,
        namespace: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        params = {
            'query': query,
            'limit': limit,
            'offset': offset
        }
        if provider:
            params['provider'] = provider
        if namespace:
            params['namespace'] = namespace
            
        response = requests.get(
            f"{self.base_url}/v1/modules/search",
            params=params,
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.json()

    def get_module_versions(self, namespace: str, name: str, provider: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/v1/modules/{namespace}/{name}/{provider}/versions",
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.json()

    def get_module_details(self, namespace: str, name: str, provider: str, version: str) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/v1/modules/{namespace}/{name}/{provider}/{version}",
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.json()

# Initialize the client
client = TerraformModuleClient(base_url=app.config['BACKEND_URL'])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def refresh_token(current_user):
    """Helper function to refresh an expired token"""
    try:
        if not current_user.token:
            return False
            
        response = requests.post(
            f"{app.config['BACKEND_URL']}/auth/refresh",
            headers={
                'Authorization': f'Bearer {current_user.token}',
                'Content-Type': 'application/json'
            }
        )
        
        if response.status_code == 401:  # Token completely invalid
            return False
            
        response.raise_for_status()
        token_data = response.json()
        
        if not token_data.get('token'):
            return False
            
        current_user.token = token_data['token']
        current_user.permissions = token_data.get('permissions', current_user.permissions)
        db.session.commit()
        client.set_jwt_token(current_user.token)
        logger.info(f"Token refreshed for user {current_user.email}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Token refresh failed: {str(e)}")
        return False

@app.before_request
def check_token():
    """Check if token needs refresh before each request"""
    if current_user.is_authenticated and request.endpoint != 'login':
        try:
            response = requests.get(
                f"{app.config['BACKEND_URL']}/auth/verify",
                headers={'Authorization': f'Bearer {current_user.token}'} if current_user.token else {}
            )
            if response.status_code == 401:  # Token expired
                if not refresh_token(current_user):
                    logout_user()
                    flash('Your session has expired. Please log in again.', 'info')
                    return redirect(url_for('login'))
        except requests.exceptions.RequestException:
            pass  # Don't fail on connection issues

@app.route('/')
def home():
    """Public homepage that redirects to login if not authenticated"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            try:
                # Request token from backend with role-based permissions
                response = requests.post(
                    f"{app.config['BACKEND_URL']}/auth/token",
                    json={
                        "username": user.email,
                        "password": form.password.data,
                        "grant_type": "password",
                        "scope": " ".join(user.permissions),
                        "role": user.role
                    },
                    headers={'Content-Type': 'application/json'}
                )
                logger.debug(f"Token request status: {response.status_code}")
                
                if response.status_code == 403:
                    logger.error(f"Authentication failed for user {user.email}")
                    flash('Authentication failed. Please check your credentials.', 'danger')
                    return render_template('login.html', form=form)
                
                response.raise_for_status()
                token_data = response.json()
                
                if not token_data.get('token'):
                    logger.error(f"No token in response: {token_data}")
                    flash('Authentication failed: Invalid server response', 'danger')
                    return render_template('login.html', form=form)
                
                # Update permissions from token response if they changed
                if 'permissions' in token_data:
                    user.permissions = token_data['permissions']
                    logger.info(f"Updated permissions for user {user.email}: {user.permissions}")
                
                # Store token and update client
                user.token = token_data['token']
                db.session.commit()
                client.set_jwt_token(user.token)
                
                # Complete login
                login_user(user)
                logger.info(f"User {user.email} logged in successfully with role {user.role}")
                
                next_page = request.args.get('next')
                if not next_page or urlparse(next_page).netloc != '':
                    next_page = url_for('index')
                return redirect(next_page)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Backend authentication failed: {str(e)}")
                flash('Authentication service unavailable. Please try again later.', 'danger')
                return render_template('login.html', form=form)
            except Exception as e:
                logger.error(f"Unexpected error during login: {str(e)}")
                flash('An unexpected error occurred. Please try again.', 'danger')
                return render_template('login.html', form=form)
        
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

        # Check if this is the first user (admin)
        is_first_user = User.query.count() == 0
        admin_email = os.environ.get('ADMIN_EMAIL')
        
        if is_first_user and form.email.data == admin_email:
            # First user with matching admin email gets admin role
            role = 'admin'
            permissions = ['read:module', 'write:module', 'upload:module', 'admin:users']
        else:
            # All other users get basic user role with read permission only
            role = 'user'
            permissions = ['read:module']
        
        user = User(
            email=form.email.data,
            role=role,
            permissions=permissions
        )
        user.set_password(form.password.data)
        user.namespaces = []
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/register_repo', methods=['GET', 'POST'])
@login_required
def register_repo():
    # Check if user has permission to register repositories
    if 'upload:module' not in current_user.permissions:
        flash('You do not have permission to register repositories. Please upgrade to Publisher role.', 'danger')
        return redirect(url_for('index'))

    form = RepositoryForm()
    if form.validate_on_submit():
        repo_url = form.repo_url.data.rstrip('.git')
        
        # Extract namespace and name from GitHub URL
        match = re.match(r'^https?://github\.com/([\w-]+)/([\w-]+)', repo_url)
        if not match:
            flash('Invalid GitHub repository URL format.', 'danger')
            return render_template('register_repo.html', form=form)
            
        namespace = match.group(1)
        name = match.group(2)
        
        # Check if user has permission for this namespace
        if namespace not in (current_user.namespaces or DEFAULT_NAMESPACES):
            flash(f'You do not have permission to register repositories in the {namespace} namespace.', 'danger')
            return render_template('register_repo.html', form=form)
        
        # Check if repository already exists
        existing_repo = Repository.query.filter_by(
            namespace=namespace,
            name=name
        ).first()
        
        if existing_repo:
            flash('This repository has already been registered.', 'warning')
            return redirect(url_for('index'))
        
        # Create new repository
        repo = Repository(
            url=repo_url,
            namespace=namespace,
            name=name,
            provider='github',
            owner_id=current_user.id
        )
        
        try:
            db.session.add(repo)
            db.session.commit()
            flash('Repository registered successfully.', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error registering repository: {str(e)}', 'danger')
            return render_template('register_repo.html', form=form)
    
    return render_template('register_repo.html', form=form)

@app.route('/api/repositories')
@login_required
def list_repositories():
    try:
        # Get all repositories in namespaces the user has access to
        repositories = Repository.query.filter(
            Repository.namespace.in_(current_user.namespaces or DEFAULT_NAMESPACES)
        ).all()
        
        repos_list = [{
            'id': repo.id,
            'url': repo.url,
            'namespace': repo.namespace,
            'name': repo.name,
            'provider': repo.provider,
            'owner': repo.owner_id,
            'created_at': repo.created_at.isoformat(),
            'updated_at': repo.updated_at.isoformat(),
            'can_edit': repo.owner_id == current_user.id  # Add flag for UI to show edit controls
        } for repo in repositories]
        return jsonify({'repositories': repos_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/v1/modules/search')
@login_required
def search_modules():
    try:
        query = request.args.get('query', '')
        provider = request.args.get('provider')
        namespace = request.args.get('namespace')
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)

        # If namespace is specified, verify user has access to it
        if namespace and namespace not in (current_user.namespaces or DEFAULT_NAMESPACES):
            return jsonify({"error": "Namespace access denied"}), 403
        
        result = client.search_modules(
            query=query,
            provider=provider,
            namespace=namespace,
            limit=limit,
            offset=offset
        )
        
        # Filter results to only show modules from accessible namespaces
        if 'modules' in result:
            accessible_namespaces = current_user.namespaces or DEFAULT_NAMESPACES
            result['modules'] = [
                module for module in result['modules']
                if module.get('namespace') in accessible_namespaces
            ]
            
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error searching modules: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/v1/modules/<namespace>/<name>/<provider>/versions')
@login_required
def list_versions(namespace, name, provider):
    try:
        # Verify user has access to this namespace
        if namespace not in (current_user.namespaces or DEFAULT_NAMESPACES):
            return jsonify({"error": "Namespace access denied"}), 403
            
        result = client.list_versions(namespace, name, provider)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error listing versions: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/v1/modules/<namespace>/<name>/<provider>/<version>/download')
@login_required
def download_module(namespace, name, provider, version):
    try:
        # Verify user has access to this namespace
        if namespace not in (current_user.namespaces or DEFAULT_NAMESPACES):
            return jsonify({"error": "Namespace access denied"}), 403
            
        result = client.get_download_url(namespace, name, provider, version)
        response = Response('', 204)
        if result and 'download_url' in result:
            response.headers['X-Terraform-Get'] = result['download_url']
        return response
    except Exception as e:
        logger.error(f"Error getting download URL: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/v1/modules/<namespace>/<name>/<provider>/<version>/source')
@login_required
def get_module_source(namespace, name, provider, version):
    try:
        # Verify user has access to this namespace
        if namespace not in (current_user.namespaces or DEFAULT_NAMESPACES):
            return jsonify({"error": "Namespace access denied"}), 403
            
        result = client.get_module_source(namespace, name, provider, version)
        response = Response('', 204)
        if result and 'download_url' in result:
            response.headers['X-Terraform-Get'] = result['download_url']
        return response
    except Exception as e:
        logger.error(f"Error getting module source: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/admin/users')
@login_required
def admin_users():
    # Check if user is admin
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
        
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    # Check if user is admin
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
        
    user = User.query.get_or_404(user_id)
    form = AdminUserForm()
    
    if form.validate_on_submit():
        user.role = form.role.data
        user.permissions = [p.strip() for p in form.permissions.data.split(',') if p.strip()]
        user.namespaces = [n.strip() for n in form.namespaces.data.split(',') if n.strip()]
        
        db.session.commit()
        flash(f'User {user.email} updated successfully.', 'success')
        return redirect(url_for('admin_users'))
        
    elif request.method == 'GET':
        form.role.data = user.role
        form.permissions.data = ', '.join(user.permissions or [])
        form.namespaces.data = ', '.join(user.namespaces or [])
        
    return render_template('admin/edit_user.html', form=form, user=user)

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash('The form session has expired. Please try again.', 'danger')
    return redirect(url_for('register_repo'))

@app.errorhandler(HTTPException)
def handle_http_error(error):
    """Handle HTTP errors according to OpenAPI spec"""
    response = jsonify({
        "error": error.description,
        "status_code": error.code
    })
    response.status_code = error.code
    return response

@app.errorhandler(Exception)
def handle_generic_error(error):
    """Handle unexpected errors according to OpenAPI spec"""
    logger.error(f"Unexpected error: {str(error)}")
    response = jsonify({
        "error": "Internal server error",
        "status_code": 500
    })
    response.status_code = 500
    return response

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)