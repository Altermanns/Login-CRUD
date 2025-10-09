# LoginCRUD — Sistema básico de CRUD de Materia Prima

Proyecto Django que implementa un sistema pequeño para gestionar "Materia Prima" con autenticación y páginas protegidas.

Este README cubre cómo preparar el entorno, ejecutar la app en desarrollo, crear usuarios de prueba, y detalles importantes antes de subir a Git.

## Resumen
- Framework: Django 5.2.x
- Python: 3.11+
- Base de datos: SQLite (por defecto, `db.sqlite3` en el repo)
- App principal: `Texcore`

## Estructura principal
- `LoginCRUD/` — carpeta del proyecto (configuración de Django)
- `Texcore/` — aplicación que contiene modelos, vistas, templates y estática
	- `templates/paginas/` — plantillas base, login, dashboard
	- `templates/libros/` — vistas CRUD para Materia Prima (index, crear, editar)
	- `static/css/` — estilos (`site.css`, `login.css`)
- `manage.py` — comandos de Django
- `db.sqlite3` — base de datos de desarrollo (incluida en repo actualmente)

## Requisitos
- Python 3.11+
- pip

Recomiendo usar un entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # PowerShell
pip install -r requirements.txt  # (si agregas uno)
```

> Nota: Este repo no incluye `requirements.txt` por defecto. Puedes generar uno con `pip freeze > requirements.txt` en tu entorno.

## Migraciones
Si abres el proyecto en una máquina nueva, aplica migraciones:

```powershell
py -3 manage.py makemigrations
py -3 manage.py migrate
```

## Crear usuarios
- Crear superusuario (admin):
```powershell
py -3 manage.py createsuperuser
```
- Crear usuario de prueba (no superuser):
```powershell
py -3 manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_user('testuser','test@example.com','Testpass123!')"
```

En este repositorio de ejemplo ya creé un usuario de prueba:
- Usuario: `testuser`
- Contraseña: `Testpass123!`

## Ejecutar servidor en desarrollo
```powershell
py -3 manage.py runserver
```
Visitar: `http://127.0.0.1:8000/`

## Flujo de la app
1. Inicio (`/`) — página pública con botón "Iniciar Sesion".
2. Login (`/login/`) — autenticación; redirige al dashboard en `/libros/`.
3. Dashboard (`/libros/`) — botones a CRUD de Materia Prima.
4. CRUD (`/materias/`, `/materias/crear/`, `/materias/editar/<id>/`) — vistas protegidas con login.

## Seguridad y buenas prácticas
- Las vistas protegidas usan `@login_required` y `LOGIN_URL`/`LOGIN_REDIRECT_URL` están configurados.
- La eliminación de registros ahora se hace vía POST con CSRF (se usa un formulario pequeño en la plantilla).
- No subas `db.sqlite3` ni secretos al repositorio público. Añade `db.sqlite3` a `.gitignore` si vas a publicar el repo.
- En producción: desactivar `DEBUG`, configurar `ALLOWED_HOSTS`, usar una base de datos adecuada y configurar `SECRET_KEY` vía variables de entorno.

## Tests rápidos (manual)
- Verificar que las URLs protegidas redirigen cuando no estás autenticado:
```powershell
py -3 manage.py shell -c "from django.test import Client; c=Client(); print(c.get('/libros/').status_code)"
```

## Posibles mejoras (sugerencias)
- Refactor a Class-Based Views para el CRUD (`ListView`, `CreateView`, `UpdateView`, `DeleteView`).
- Añadir un `services.py` para separar lógica de negocio y mantener vistas delgadas.
- Añadir pruebas unitarias (pytest/django) para asegurar flujo de autenticación y CRUD.
- Añadir `requirements.txt` y un `Makefile` o scripts PowerShell para facilitar comandos comunes.

## Licencia
MIT License

Copyright (c) 2025 Isaac Trujillo & Brandon Arrellano

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


