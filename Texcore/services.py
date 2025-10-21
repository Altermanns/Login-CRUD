from typing import Optional
from django.contrib.auth import authenticate
from .models import Materia


def authenticate_user(request, username: str, password: str) -> Optional[object]:
    """Authenticate a user with given credentials. Returns the user or None.

    Small wrapper to isolate auth calls and make views simpler and testable.
    """
    return authenticate(request, username=username, password=password)


def get_all_materias():
    """Return queryset of Materia ordered by newest first."""
    return Materia.objects.all().order_by('-id')
