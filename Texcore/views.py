from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect

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
        # minimal create: read a name if provided
        new_id = max([m['id'] for m in _MATERIAS], default=0) + 1
        _MATERIAS.append({'id': new_id, 'nombre': request.POST.get('nombre', f'Materia {new_id}'),
                          'tipo': request.POST.get('tipo', ''), 'cantidad': request.POST.get('cantidad', 0),
                          'unidad_medida': request.POST.get('unidad_medida', ''), 'lote': request.POST.get('lote', ''),
                          'fecha_ingreso': request.POST.get('fecha_ingreso', '')})
        return redirect('index_materia')
    # provide a dummy form object with as_p for the template
    class DummyForm(dict):
        def as_p(self):
            return ''

    return render(request, 'libros/crear.html', {'form': DummyForm()})


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
