# 🚀 Guía de Deployment en Render con Docker y SQLite

Este documento describe cómo deployar tu aplicación TextilApp Django en Render usando Docker y SQLite.

## 📋 Preparativos

### 1. Archivos de Configuración Creados

- ✅ `Dockerfile` - Configuración de contenedor Docker con SQLite
- ✅ `docker-compose.yml` - Para desarrollo local con Docker
- ✅ `requirements.txt` - Dependencias de Python (sin PostgreSQL)
- ✅ `entrypoint.sh` - Script de inicialización simplificado
- ✅ `.dockerignore` - Archivos a ignorar en el build
- ✅ `LoginCRUD/settings/` - Configuraciones separadas por entorno

### 2. Usuarios por Defecto

El sistema creará automáticamente estos usuarios en el primer deploy:

- **Admin**: `admin` / `admin123`
- **Operario**: `operario` / `operario123`

### 3. Base de Datos

- ✅ **SQLite** incluida en el contenedor Docker
- ✅ **Persistente** - Los datos se mantienen con el contenedor
- ✅ **Sin configuración externa** - Todo funciona automáticamente

## 🔧 Pasos para Deployment en Render

### Paso 1: Preparar el Repositorio

1. **Subir código a GitHub**:
```bash
git add .
git commit -m "Add Docker configuration with SQLite for Render deployment"
git push origin main
```

### Paso 2: Crear Servicio Web en Render

1. **Ve a [render.com](https://render.com)** y crea una cuenta
2. **Conecta tu repositorio de GitHub**
3. **Crea un nuevo "Web Service"**
4. **Selecciona tu repositorio `Login-CRUD`**

### Paso 3: Configurar el Servicio

**Configuración Básica:**
- **Name**: `textilapp-django`
- **Region**: Oregon (US West) o el más cercano
- **Branch**: `main`
- **Runtime**: `Docker`

### Paso 4: Configurar Variables de Entorno (Opcional)

En la sección "Environment Variables":

#### Variables Básicas:
```bash
# Django Settings (ya configuradas por defecto)
DJANGO_SETTINGS_MODULE=LoginCRUD.settings.production
DEBUG=False

# Secret key personalizada (opcional - tiene una por defecto)
SECRET_KEY=tu-clave-secreta-super-segura-aqui

# Usuarios por defecto (opcional - personaliza si quieres)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=tu_admin_password_seguro
ADMIN_EMAIL=admin@tuempresa.com
OPERARIO_USERNAME=operario_demo
OPERARIO_PASSWORD=tu_operario_password
OPERARIO_EMAIL=operario@tuempresa.com
```

### ⚠️ **¡NO necesitas configurar base de datos!**
SQLite está incluida automáticamente en el contenedor.

### Paso 5: Deploy

1. **Haz clic en "Create Web Service"**
2. **Render comenzará el build automáticamente**
3. **El proceso tomará unos 5-7 minutos**

## 🔍 Verificación del Deploy

### 1. Revisar Logs

En tu servicio web en Render, ve a "Logs" para verificar:

```
✅ Starting Django application with SQLite...
✅ Applying database migrations...
✅ Collecting static files...
✅ Creating default users...
✅ Superuser admin created successfully
✅ Demo operario operario created successfully
✅ Starting Gunicorn web server...
```

### 2. Probar la Aplicación

Tu aplicación estará disponible en:
```
https://tu-app-name.onrender.com
```

**Usuarios de prueba**:
- Admin: `admin` / `admin123` (o los que configuraste)
- Operario: `operario` / `operario123` (o los que configuraste)

## 🏠 Desarrollo Local con Docker

Si quieres probar todo localmente con Docker:

```bash
# Construir y ejecutar con PostgreSQL
docker-compose up --build

# Solo construir la imagen
docker build -t textilapp .

# Ejecutar solo el contenedor
docker run -p 8000:8000 textilapp
```

## 🛠️ Comandos Útiles

### Crear usuarios adicionales en producción:

1. **Accede al shell de Django en Render** (desde los logs o terminal):
```python
from django.contrib.auth.models import User
from Texcore.models import Profile

# Crear nuevo admin
admin = User.objects.create_superuser('nuevo_admin', 'admin@empresa.com', 'password')
profile = Profile.objects.create(user=admin, role='admin')

# Crear nuevo operario
operario = User.objects.create_user('nuevo_operario', 'operario@empresa.com', 'password')
profile = Profile.objects.create(user=operario, role='operario')
```

### Ejecutar migraciones manualmente:
```bash
# En el shell de tu servicio en Render
python manage.py migrate
```

## 🔒 Configuraciones de Seguridad

En producción, tu app tendrá automáticamente:

- ✅ HTTPS habilitado por Render
- ✅ Static files servidos por WhiteNoise
- ✅ Base de datos SQLite incluida en el contenedor
- ✅ Variables de entorno protegidas
- ✅ Configuraciones de seguridad Django activadas

## 📞 Solución de Problemas

### Build Errors:
- Verifica que el `Dockerfile` esté en la raíz del proyecto
- Revisa que `requirements.txt` tenga todas las dependencias
- Asegúrate de que Docker Desktop esté ejecutándose para pruebas locales

### Database Errors:
- SQLite está incluida automáticamente, no necesita configuración
- Si hay problemas, verifica que `db.sqlite3` esté en el proyecto
- Las migraciones se ejecutan automáticamente en el entrypoint

### Static Files Issues:
- Los archivos estáticos se colectan automáticamente en el build
- WhiteNoise se encarga de servirlos en producción
- Verifica que el directorio `Texcore/static/css/` exista

### Application Errors:
- Revisa los logs en tiempo real desde el dashboard de Render
- Verifica que todas las variables de entorno estén configuradas
- Usuarios por defecto se crean automáticamente (admin/operario)

## 🎯 URLs de la Aplicación

Una vez deployada:

- **Home**: `https://tu-app.onrender.com/`
- **Login**: `https://tu-app.onrender.com/login/`
- **Admin Dashboard**: `https://tu-app.onrender.com/dashboard/admin/`
- **Operario Dashboard**: `https://tu-app.onrender.com/dashboard/operario/`
- **Django Admin**: `https://tu-app.onrender.com/admin/`

¡Tu aplicación TextilApp estará lista para producción! 🎉

## 🔄 Actualizaciones Aplicadas (Última versión)

Este deployment incluye todas las mejoras y correcciones:

- ✅ **Sistema de roles**: Admin y Operario completamente funcional
- ✅ **Base de datos SQLite**: Incluida en el contenedor, persistente
- ✅ **Debugging removido**: Código limpio para producción
- ✅ **Directorios static**: Creados automáticamente
- ✅ **Permisos de archivos**: Configurados correctamente
- ✅ **Entrypoint robusto**: Con manejo de errores mejorado
- ✅ **Usuarios automáticos**: Admin y operario creados en el primer deploy
- ✅ **Validación de datos**: Persistencia confirmada y funcional

### Comandos para deployment final:

```bash
# 1. Asegurar que Docker Desktop esté ejecutándose
# 2. Probar localmente (opcional)
docker build -t textilapp .
docker run -p 8000:8000 textilapp

# 3. Subir a GitHub
git add .
git commit -m "Final Docker update with all fixes for Render deployment"
git push origin main

# 4. Deploy en Render usando tu repositorio GitHub
```

¡Listo para Render! 🚀