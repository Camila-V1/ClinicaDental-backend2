"""
Comando Django para actualizar bitácoras sin usuario.
Uso: python manage.py asignar_usuarios_bitacora --tenant=clinica_demo
"""

from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from reportes.models import BitacoraAccion
from usuarios.models import Usuario


class Command(BaseCommand):
    help = 'Asigna el usuario admin a las bitácoras que no tienen usuario'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant',
            type=str,
            default='clinica_demo',
            help='Schema del tenant (default: clinica_demo)'
        )
        parser.add_argument(
            '--admin-email',
            type=str,
            default='admin@clinica-demo.com',
            help='Email del usuario admin (default: admin@clinica-demo.com)'
        )

    def handle(self, *args, **options):
        tenant_schema = options['tenant']
        admin_email = options['admin_email']
        
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("🔄 ACTUALIZANDO BITÁCORAS SIN USUARIO"))
        self.stdout.write("=" * 70)
        self.stdout.write(f"\n📍 Tenant: {tenant_schema}")
        self.stdout.write(f"📧 Admin email: {admin_email}\n")
        
        with schema_context(tenant_schema):
            # Obtener el usuario admin
            try:
                admin = Usuario.objects.filter(
                    email=admin_email,
                    tipo_usuario='ADMIN'
                ).first()
                
                if not admin:
                    self.stdout.write(self.style.ERROR(
                        f"❌ No se encontró usuario admin con email {admin_email}"
                    ))
                    return
                
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Usuario admin encontrado: {admin.full_name} (ID: {admin.id})"
                ))
                
                # Obtener bitácoras sin usuario
                bitacoras_sin_usuario = BitacoraAccion.objects.filter(usuario__isnull=True)
                total = bitacoras_sin_usuario.count()
                
                self.stdout.write(f"\n📋 {total} registros de bitácora sin usuario")
                
                if total == 0:
                    self.stdout.write(self.style.SUCCESS("✅ No hay registros para actualizar"))
                    return
                
                self.stdout.write("\n🔄 Actualizando registros...\n")
                
                # Actualizar en lote para mejor performance
                actualizados = bitacoras_sin_usuario.update(usuario=admin)
                
                self.stdout.write("\n" + "=" * 70)
                self.stdout.write(self.style.SUCCESS(
                    f"✅ COMPLETADO: {actualizados} registros actualizados"
                ))
                self.stdout.write("=" * 70)
                
                # Verificar
                sin_usuario = BitacoraAccion.objects.filter(usuario__isnull=True).count()
                con_usuario = BitacoraAccion.objects.filter(usuario__isnull=False).count()
                
                self.stdout.write(f"\n📊 Registros con usuario: {con_usuario}")
                self.stdout.write(f"📊 Registros sin usuario: {sin_usuario}")
                
                # Mostrar algunos ejemplos
                self.stdout.write("\n" + "=" * 70)
                self.stdout.write("ÚLTIMOS 5 REGISTROS ACTUALIZADOS:")
                self.stdout.write("=" * 70)
                
                for bitacora in BitacoraAccion.objects.filter(usuario=admin).order_by('-fecha_hora')[:5]:
                    self.stdout.write(f"\n#{bitacora.id} - {bitacora.accion}")
                    self.stdout.write(f"   Usuario: {bitacora.usuario.full_name}")
                    self.stdout.write(f"   Descripción: {bitacora.descripcion[:60]}...")
                    self.stdout.write(f"   Fecha: {bitacora.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')}")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"\n❌ Error: {e}"))
                import traceback
                self.stdout.write(traceback.format_exc())
