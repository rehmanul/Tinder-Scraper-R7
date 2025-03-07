import os
import logging
import secrets
from functools import wraps
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable

from flask import Flask, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)

class Auth:
    """Authentication and security functionality for the Tinder Scraper application."""
    
    def __init__(self, app: Flask):
        """Initialize the Auth module.
        
        Args:
            app: Flask application instance
        """
        self.app = app
        self.users = {}  # In a real app, this would be a database
        
        # Load admin user from environment variables
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'password')
        
        # Add admin user to the users dictionary
        self.users[admin_username] = {
            'username': admin_username,
            'password_hash': generate_password_hash(admin_password),
            'is_admin': True,
            'last_login': None
        }
        
        # Register routes with the app
        self._register_routes()
    
    def _register_routes(self):
        """Register authentication routes with the Flask app."""
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            # Handle login logic
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')
                
                if not username or not password:
                    flash('Username and password are required', 'error')
                    return redirect(url_for('login'))
                
                user = self.users.get(username)
                
                if not user or not check_password_hash(user['password_hash'], password):
                    flash('Invalid username or password', 'error')
                    return redirect(url_for('login'))
                
                # Login successful
                session['user_id'] = username
                session['is_admin'] = user['is_admin']
                session['logged_in'] = True
                
                # Update last login time
                self.users[username]['last_login'] = datetime.now()
                
                return redirect(url_for('index'))
            
            # GET request - show login form
            return '''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Login - Tinder Scraper</title>
                    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
                    <style>
                        :root {
                            --primary-color: #fe3c72;
                            --primary-gradient: linear-gradient(135deg, #fe3c72, #ff655b);
                            --background-color: #f8f9fa;
                            --text-color: #212121;
                            --border-color: #e0e0e0;
                        }
                        
                        body {
                            font-family: 'Inter', sans-serif;
                            background-color: var(--background-color);
                            color: var(--text-color);
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            margin: 0;
                        }
                        
                        .login-container {
                            background-color: white;
                            border-radius: 12px;
                            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                            padding: 32px;
                            width: 320px;
                        }
                        
                        .login-logo {
                            text-align: center;
                            margin-bottom: 24px;
                        }
                        
                        .login-logo h1 {
                            margin: 0;
                            font-size: 24px;
                            font-weight: 600;
                            background: var(--primary-gradient);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                        }
                        
                        .login-form {
                            display: flex;
                            flex-direction: column;
                        }
                        
                        .form-group {
                            margin-bottom: 16px;
                        }
                        
                        .form-group label {
                            display: block;
                            margin-bottom: 8px;
                            font-size: 14px;
                            font-weight: 500;
                        }
                        
                        .form-group input {
                            width: 100%;
                            padding: 10px 12px;
                            border: 1px solid var(--border-color);
                            border-radius: 6px;
                            font-size: 14px;
                        }
                        
                        .login-button {
                            background: var(--primary-gradient);
                            color: white;
                            border: none;
                            border-radius: 8px;
                            padding: 12px;
                            font-size: 16px;
                            font-weight: 500;
                            cursor: pointer;
                            transition: all 0.3s ease;
                        }
                        
                        .login-button:hover {
                            transform: translateY(-2px);
                            box-shadow: 0 4px 8px rgba(254, 60, 114, 0.3);
                        }
                        
                        .flash-messages {
                            margin-bottom: 16px;
                        }
                        
                        .flash-error {
                            background-color: #ffebee;
                            color: #c62828;
                            padding: 8px 12px;
                            border-radius: 4px;
                            font-size: 14px;
                        }
                    </style>
                </head>
                <body>
                    <div class="login-container">
                        <div class="login-logo">
                            <h1>Tinder Scraper</h1>
                        </div>
                        
                        <div class="flash-messages">
                            {% for category, message in get_flashed_messages(with_categories=true) %}
                                <div class="flash-{{ category }}">{{ message }}</div>
                            {% endfor %}
                        </div>
                        
                        <form class="login-form" method="post" action="/login">
                            <div class="form-group">
                                <label for="username">Username</label>
                                <input type="text" id="username" name="username" required>
                            </div>
                            
                            <div class="form-group">
                                <label for="password">Password</label>
                                <input type="password" id="password" name="password" required>
                            </div>
                            
                            <button type="submit" class="login-button">Log In</button>
                        </form>
                    </div>
                </body>
                </html>
            '''
        
        @self.app.route('/logout')
        def logout():
            # Clear session data
            session.clear()
            return redirect(url_for('login'))
        
        @self.app.route('/api/auth/check')
        def auth_check():
            # Check if user is authenticated
            if session.get('logged_in'):
                return jsonify({
                    'authenticated': True,
                    'username': session.get('user_id'),
                    'is_admin': session.get('is_admin', False)
                })
            else:
                return jsonify({
                    'authenticated': False
                })
    
    def login_required(self, f: Callable) -> Callable:
        """Decorator to require login for a route.
        
        Args:
            f: Function to decorate
            
        Returns:
            Callable: Decorated function
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('logged_in'):
                return redirect(url_for('login', next=request.url))
            return f(*args, **kwargs)
        return decorated_function
    
    def admin_required(self, f: Callable) -> Callable:
        """Decorator to require admin privileges for a route.
        
        Args:
            f: Function to decorate
            
        Returns:
            Callable: Decorated function
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('logged_in') or not session.get('is_admin'):
                return redirect(url_for('login', next=request.url))
            return f(*args, **kwargs)
        return decorated_function
    
    def create_user(self, username: str, password: str, is_admin: bool = False) -> bool:
        """Create a new user.
        
        Args:
            username: Username for the new user
            password: Password for the new user
            is_admin: Whether the user should have admin privileges
            
        Returns:
            bool: True if user was created successfully, False otherwise
        """
        if username in self.users:
            return False
        
        self.users[username] = {
            'username': username,
            'password_hash': generate_password_hash(password),
            'is_admin': is_admin,
            'last_login': None
        }
        
        return True
    
    def change_password(self, username: str, new_password: str) -> bool:
        """Change a user's password.
        
        Args:
            username: Username of the user
            new_password: New password for the user
            
        Returns:
            bool: True if password was changed successfully, False otherwise
        """
        if username not in self.users:
            return False
        
        self.users[username]['password_hash'] = generate_password_hash(new_password)
        return True
    
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user with username and password.
        
        Args:
            username: Username to authenticate
            password: Password to authenticate
            
        Returns:
            Optional[Dict[str, Any]]: User data if authentication was successful, None otherwise
        """
        user = self.users.get(username)
        
        if not user or not check_password_hash(user['password_hash'], password):
            return None
        
        # Update last login time
        self.users[username]['last_login'] = datetime.now()
        
        return user
    
    def generate_api_key(self, username: str) -> Optional[str]:
        """Generate a new API key for a user.
        
        Args:
            username: Username to generate API key for
            
        Returns:
            Optional[str]: Generated API key if successful, None otherwise
        """
        if username not in self.users:
            return None
        
        # Generate a random API key
        api_key = secrets.token_hex(16)
        
        # Store the API key with the user
        self.users[username]['api_key'] = api_key
        
        return api_key
    
    def validate_api_key(self, api_key: str) -> Optional[str]:
        """Validate an API key and return the associated username.
        
        Args:
            api_key: API key to validate
            
        Returns:
            Optional[str]: Username associated with the API key if valid, None otherwise
        """
        for username, user_data in self.users.items():
            if user_data.get('api_key') == api_key:
                return username
        
        return None
