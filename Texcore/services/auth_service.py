"""
Authentication service - handles user authentication logic.
"""
from typing import Optional
from django.contrib.auth import authenticate
from django.contrib.auth.models import User


def authenticate_user(request, username: str, password: str) -> Optional[User]:
    """
    Authenticate a user with given credentials.
    
    Args:
        request: Django request object
        username: Username to authenticate
        password: Password to authenticate
        
    Returns:
        User object if authentication successful, None otherwise
    """
    return authenticate(request, username=username, password=password)
