from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import MateriaForm
from .models import Materia

def inicio(request):
    # Landing page: public, minimal actions
    return render(request, 'paginas/inicio.html')

def login(request):
    # Handle authentication: POST attempts to authenticate and redirect to dashboard
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Usuario o contraseña inválidos')
            return redirect('login')
    return render(request, 'paginas/login.html')


@login_required
def index(request):
    # Dashboard
    return render(request, 'paginas/dashboard.html')


@login_required
def index_materia(request):
    materias = Materia.objects.all().order_by('-id')
    return render(request, 'libros/index.html', {'materias': materias})


@login_required
def crear_materia(request):
    if request.method == 'POST':
        form = MateriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index_materia')
    else:
        form = MateriaForm()
    return render(request, 'libros/crear.html', {'form': form})


@login_required
def editar_materia(request, materia_id):
    materia = get_object_or_404(Materia, pk=materia_id)
    if request.method == 'POST':
        form = MateriaForm(request.POST, instance=materia)
        if form.is_valid():
            form.save()
            return redirect('index_materia')
    else:
        form = MateriaForm(instance=materia)
    return render(request, 'libros/editar.html', {'form': form})


@login_required
@require_POST
def eliminar_materia(request, materia_id):
    materia = get_object_or_404(Materia, pk=materia_id)
    materia.delete()
    messages.success(request, 'Materia eliminada correctamente.')
    return redirect('index_materia')


def editar_materia_no_id(request):
    """Handle requests to /materias/editar/ without an ID: redirect to index."""
    return redirect('index_materia')


def logout(request):
    auth_logout(request)
    return redirect('inicio')
