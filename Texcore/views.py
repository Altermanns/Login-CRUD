from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from .forms import CreateMateriaForm

# Minimal in-memory materias storage to make templates work without a model
_MATERIAS = []

def inicio(request):
    return render(request, 'paginas/inicio.html')
def login(request):
    return render(request, 'paginas/login.html')
def index(request):
    return render(request, 'libros/index.html')


def index_materia(request):
    # Provide list of materias (empty if none)
    return render(request, 'libros/index.html', {'materias': _MATERIAS})


def crear_materia(request):
    if request.method == 'POST':
        form = CreateMateriaForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            new_id = max([m['id'] for m in _MATERIAS], default=0) + 1
            _MATERIAS.append({
                'id': new_id,
                'nombre': data.get('nombre'),
                'tipo': data.get('tipo'),
                'cantidad': data.get('cantidad') or 0,
                'unidad_medida': data.get('unidad_medida'),
                'lote': data.get('lote'),
                'fecha_ingreso': data.get('fecha_ingreso') and str(data.get('fecha_ingreso')) or ''
            })
            return redirect('index_materia')
    else:
        form = CreateMateriaForm()

    return render(request, 'libros/crear.html', {'form': form})


def editar_materia(request, materia_id):
    materia = next((m for m in _MATERIAS if m['id'] == int(materia_id)), None)
    if request.method == 'POST':
        if materia:
            materia['nombre'] = request.POST.get('nombre', materia.get('nombre', ''))
        return redirect('index_materia')
    # build dummy form
    class DummyForm(dict):
        def as_p(self):
            html = ''
            if materia:
                for k, v in materia.items():
                    html += f'<p><label>{k}</label><input name="{k}" value="{v}"></p>'
            return html

    return render(request, 'libros/editar.html', {'form': DummyForm()})


def eliminar_materia(request, materia_id):
    global _MATERIAS
    _MATERIAS = [m for m in _MATERIAS if m['id'] != int(materia_id)]
    return redirect('index_materia')
