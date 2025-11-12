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
    
    try:
        # Verificar si ya hay datos
        if Materia.objects.exists():
            print("🔄 Ya existen datos en la base de datos, saltando inicialización...")
            return
        
        print("📦 Creando datos de muestra...")
        
        # Obtener usuarios admin, operario y preparador
        try:
            admin_user = User.objects.get(username='admin')
            operario_user = User.objects.get(username='operario')
            
            # Intentar obtener preparador, crear si no existe
            try:
                preparador_user = User.objects.get(username='preparador')
            except User.DoesNotExist:
                preparador_user = User.objects.create_user(
                    username='preparador',
                    email='preparador@textilapp.com',
                    password='preparador123',
                    first_name='Demo',
                    last_name='Preparador'
                )
                profile, created = Profile.objects.get_or_create(user=preparador_user)
                profile.role = 'preparador'
                profile.save()
                print("✅ Usuario preparador creado automáticamente")
                
        except User.DoesNotExist:
            print("❌ Los usuarios admin/operario no existen. Ejecute la creación de usuarios primero.")
            return
        
        # Datos de muestra para materias
        materias_muestra = [
            {
                'tipo': 'ALGODON',
                'cantidad': 150,
                'unidad_medida': 'kg',
                'lote': 'ALG-2024-001',
                'usuario_registro': operario_user,
                'fecha_ingreso': date.today() - timedelta(days=5)
            },
            {
                'tipo': 'SEDA',
                'cantidad': 75,
                'unidad_medida': 'kg',
                'lote': 'SED-2024-001',
                'usuario_registro': operario_user,
                'fecha_ingreso': date.today() - timedelta(days=3)
            },
            {
                'tipo': 'LANA',
                'cantidad': 200,
                'unidad_medida': 'kg',
                'lote': 'LAN-2024-001',
                'usuario_registro': operario_user,
                'fecha_ingreso': date.today() - timedelta(days=2)
            },
            {
                'tipo': 'POLIESTER',
                'cantidad': 300,
                'unidad_medida': 'kg',
                'lote': 'POL-2024-001',
                'usuario_registro': operario_user,
                'fecha_ingreso': date.today() - timedelta(days=1)
            },
        ]
        
        # Crear las materias de muestra
        for materia_data in materias_muestra:
            try:
                materia = Materia.objects.create(**materia_data)
                print(f"✅ Creada materia: {materia.tipo} - {materia.cantidad}{materia.unidad_medida} - Lote: {materia.lote}")
            except Exception as e:
                print(f"⚠️ Error creando materia {materia_data['tipo']}: {e}")
                continue
        
        total_created = Materia.objects.count()
        print(f"🎉 Se crearon {total_created} materias de muestra exitosamente!")
        
    except Exception as e:
        print(f"❌ Error general en la inicialización de datos: {e}")
        # No lanzar la excepción para que no falle el deploy
        return

if __name__ == '__main__':
    create_sample_data()