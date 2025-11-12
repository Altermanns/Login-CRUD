#!/usr/bin/env python
"""
Script para inicializar datos de prueba en la base de datos
Se ejecuta automáticamente en el entrypoint si no hay datos
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LoginCRUD.settings.production')
django.setup()

from django.contrib.auth.models import User
from Texcore.models import Profile, Materia
from datetime import date, timedelta

def create_sample_data():
    """Crea datos de muestra para la aplicación"""
    
    # Verificar si ya hay datos
    if Materia.objects.exists():
        print("🔄 Ya existen datos en la base de datos, saltando inicialización...")
        return
    
    print("📦 Creando datos de muestra...")
    
    # Obtener usuarios admin y operario
    try:
        admin_user = User.objects.get(username='admin')
        operario_user = User.objects.get(username='operario')
    except User.DoesNotExist:
        print("❌ Los usuarios admin/operario no existen. Ejecute la creación de usuarios primero.")
        return
    
    # Datos de muestra para materias
    materias_muestra = [
        {
            'tipo': 'ALGODON',
            'cantidad': 150.5,
            'proveedor': 'Textiles del Norte SA',
            'observaciones': 'Algodón de primera calidad, fibra larga',
            'usuario_registro': operario_user,
            'fecha_ingreso': date.today() - timedelta(days=5)
        },
        {
            'tipo': 'SEDA',
            'cantidad': 75.0,
            'proveedor': 'Sedas Finas Ltda',
            'observaciones': 'Seda natural importada, color blanco',
            'usuario_registro': operario_user,
            'fecha_ingreso': date.today() - timedelta(days=3)
        },
        {
            'tipo': 'LANA',
            'cantidad': 200.0,
            'proveedor': 'Lanas Andinas',
            'observaciones': 'Lana merino de alta calidad',
            'usuario_registro': operario_user,
            'fecha_ingreso': date.today() - timedelta(days=2)
        },
        {
            'tipo': 'POLIESTER',
            'cantidad': 300.0,
            'proveedor': 'Sintéticos Modernos SA',
            'observaciones': 'Poliéster reciclado, certificado eco-friendly',
            'usuario_registro': operario_user,
            'fecha_ingreso': date.today() - timedelta(days=1)
        },
    ]
    
    # Crear las materias de muestra
    for materia_data in materias_muestra:
        materia = Materia.objects.create(**materia_data)
        print(f"✅ Creada materia: {materia.tipo} - {materia.cantidad}kg")
    
    print(f"🎉 Se crearon {len(materias_muestra)} materias de muestra exitosamente!")

if __name__ == '__main__':
    create_sample_data()