#!/usr/bin/env python
import os
import sys

# Configurar Django ANTES de importar modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LoginCRUD.settings.development')

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from Texcore.models import Materia, Profile

def test_form_submission():
    print("🧪 INICIANDO PRUEBA DE FORMULARIO")
    
    # Crear cliente de prueba
    client = Client()
    
    # Obtener usuario operario
    try:
        operario = User.objects.get(username='operario')
        print(f"✅ Usuario operario encontrado: {operario.username}")
    except User.DoesNotExist:
        print("❌ Usuario operario no encontrado")
        return
    
    # Hacer login
    login_success = client.login(username='operario', password='operario123')
    print(f"🔐 Login exitoso: {login_success}")
    
    if not login_success:
        print("❌ No se pudo hacer login")
        return
    
    # Datos del formulario
    form_data = {
        'tipo': 'Test Material Web',
        'cantidad': 100,
        'unidad_medida': 'kg',
        'lote': 'WEB001',
        'fecha_ingreso': '2025-11-11'
    }
    
    print(f"📋 Datos a enviar: {form_data}")
    
    # Contar materias antes
    count_before = Materia.objects.count()
    print(f"📊 Materias antes: {count_before}")
    
    # Enviar formulario
    response = client.post('/materias/crear/', form_data)
    
    print(f"🌐 Status code: {response.status_code}")
    print(f"📍 Redirect URL: {response.url if response.status_code in [301, 302] else 'No redirect'}")
    
    # Contar materias después
    count_after = Materia.objects.count()
    print(f"📊 Materias después: {count_after}")
    
    if count_after > count_before:
        print("✅ ¡ÉXITO! La materia se guardó correctamente")
        # Mostrar la última materia creada
        ultima = Materia.objects.order_by('-id').first()
        print(f"📦 Última materia: {ultima.tipo} - {ultima.cantidad} {ultima.unidad_medida}")
    else:
        print("❌ ERROR: La materia no se guardó")
        print("📋 Contenido de respuesta:")
        print(response.content.decode()[:500])

if __name__ == '__main__':
    test_form_submission()