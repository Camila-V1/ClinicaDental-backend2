#!/usr/bin/env python
"""
Script para probar los KPIs completos del dashboard después de las mejoras.

Valida que el endpoint /api/reportes/reportes/dashboard-kpis/ retorne
todos los 10 KPIs esperados por el frontend.

Uso:
    python test_kpis_completos.py
"""

import django
import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django_tenants.utils import schema_context

Usuario = get_user_model()

def test_kpis_completos():
    """Probar que el endpoint de KPIs retorne todos los valores esperados"""
    
    print("\n" + "="*70)
    print("🧪 TEST: KPIs Completos del Dashboard")
    print("="*70)
    
    # Usar el schema de clinica_demo
    schema_name = 'clinica_demo'
    
    with schema_context(schema_name):
        print(f"\n📋 Usando schema: {schema_name}")
        
        # Crear cliente API
        client = APIClient()
        
        # Obtener un usuario administrador
        try:
            admin = Usuario.objects.filter(
                tipo_usuario='ADMIN',
                is_active=True
            ).first()
            
            if not admin:
                print("❌ No se encontró un usuario administrador activo")
                return
            
            print(f"👤 Usuario: {admin.email}")
            
            # Autenticar
            client.force_authenticate(user=admin)
            
            # Hacer request al endpoint
            # IMPORTANTE: La URL correcta es /api/reportes/reportes/dashboard-kpis/
            # porque el router registra 'reportes' y luego el @action agrega el path
            response = client.get('/api/reportes/reportes/dashboard-kpis/', 
                                 HTTP_HOST='clinica-demo.localhost')
            
            print(f"\n📡 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Respuesta exitosa - {len(data)} KPIs recibidos\n")
                
                # Mostrar todos los KPIs
                print("📊 KPIs Retornados:")
                print("-" * 70)
                
                kpis_esperados = [
                    "Pacientes Activos",
                    "Citas Hoy",
                    "Ingresos Este Mes",
                    "Saldo Pendiente",
                    "Tratamientos Activos",
                    "Planes Completados",
                    "Promedio por Factura",
                    "Facturas Vencidas",
                    "Total Procedimientos",
                    "Pacientes Nuevos Mes"
                ]
                
                kpis_recibidos = []
                
                for item in data:
                    etiqueta = item.get('etiqueta', 'Sin etiqueta')
                    valor = item.get('valor', 0)
                    
                    # Formatear valor
                    if isinstance(valor, (int, float)):
                        if 'Ingresos' in etiqueta or 'Saldo' in etiqueta or 'Promedio' in etiqueta:
                            valor_str = f"Bs. {valor:,.2f}"
                        else:
                            valor_str = f"{valor}"
                    else:
                        valor_str = str(valor)
                    
                    print(f"  • {etiqueta:30s}: {valor_str}")
                    kpis_recibidos.append(etiqueta)
                
                # Verificar que todos los KPIs esperados estén presentes
                print("\n🔍 Validación de KPIs:")
                print("-" * 70)
                
                faltantes = []
                for esperado in kpis_esperados:
                    if esperado in kpis_recibidos:
                        print(f"  ✅ {esperado}")
                    else:
                        print(f"  ❌ {esperado} - FALTANTE")
                        faltantes.append(esperado)
                
                if faltantes:
                    print(f"\n⚠️  Faltan {len(faltantes)} KPIs:")
                    for kpi in faltantes:
                        print(f"     - {kpi}")
                else:
                    print("\n✅ ¡Todos los KPIs están presentes!")
                
                # Verificar que ningún KPI esté en 0 (si hay datos)
                print("\n💰 Análisis de Valores:")
                print("-" * 70)
                
                kpis_en_cero = []
                for item in data:
                    etiqueta = item.get('etiqueta', 'Sin etiqueta')
                    valor = item.get('valor', 0)
                    
                    if valor == 0 or valor == 0.0:
                        kpis_en_cero.append(etiqueta)
                
                if kpis_en_cero:
                    print("⚠️  KPIs con valor 0:")
                    for kpi in kpis_en_cero:
                        print(f"     - {kpi}")
                    print("\n   Esto puede ser normal si no hay datos de ese tipo.")
                else:
                    print("✅ Todos los KPIs tienen valores > 0")
                
                # Resumen
                print("\n" + "="*70)
                print("📝 RESUMEN:")
                print("="*70)
                print(f"  Total KPIs esperados: {len(kpis_esperados)}")
                print(f"  Total KPIs recibidos: {len(kpis_recibidos)}")
                print(f"  KPIs faltantes: {len(faltantes)}")
                print(f"  KPIs en cero: {len(kpis_en_cero)}")
                
                if len(faltantes) == 0 and len(kpis_en_cero) < len(kpis_esperados):
                    print("\n✅ TEST EXITOSO - El endpoint está funcionando correctamente")
                elif len(faltantes) == 0:
                    print("\n⚠️  TEST PARCIAL - Endpoint completo pero sin datos")
                else:
                    print("\n❌ TEST FALLIDO - Faltan KPIs en el endpoint")
                
            else:
                print(f"❌ Error en el request: {response.status_code}")
                print(f"   Respuesta: {response.content.decode()[:200]}")
                
        except Exception as e:
            print(f"\n❌ Error durante el test: {e}")
            import traceback
            traceback.print_exc()
    
    print("="*70 + "\n")

if __name__ == '__main__':
    test_kpis_completos()
