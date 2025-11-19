import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django_tenants.utils import schema_context
from facturacion.models import Factura
from usuarios.models import Usuario, PerfilPaciente

with schema_context('clinica_demo'):
    # Obtener el usuario
    user = Usuario.objects.get(email='paciente1@test.com')
    print(f"👤 Usuario: {user.nombre} {user.apellido}")
    print(f"   ID: {user.id}")
    print(f"   Email: {user.email}")
    print(f"   Tipo: {user.tipo_usuario}")
    
    # Verificar perfil_paciente
    print(f"\n🔍 Verificando perfil_paciente:")
    print(f"   hasattr(user, 'perfil_paciente'): {hasattr(user, 'perfil_paciente')}")
    
    if hasattr(user, 'perfil_paciente'):
        perfil = user.perfil_paciente
        print(f"   ✅ Perfil encontrado:")
        print(f"      usuario_id: {perfil.usuario_id}")
        print(f"      Dirección en memoria: {id(perfil)}")
        
        # Buscar facturas con este perfil
        facturas_perfil = Factura.objects.filter(paciente=perfil)
        print(f"\n💰 Facturas con paciente=perfil: {facturas_perfil.count()}")
        
        # Buscar facturas con usuario_id
        facturas_usuario_id = Factura.objects.filter(paciente__usuario_id=user.id)
        print(f"💰 Facturas con paciente__usuario_id={user.id}: {facturas_usuario_id.count()}")
        
        # Listar TODOS los PerfilPaciente
        print(f"\n📋 TODOS los PerfilPaciente en el sistema:")
        for p in PerfilPaciente.objects.all():
            print(f"   - usuario_id={p.usuario_id}, Usuario: {p.usuario.email if p.usuario else 'Sin usuario'}")
        
        # Listar TODAS las facturas con sus pacientes
        print(f"\n📋 TODAS las Facturas en el sistema:")
        for f in Factura.objects.all():
            if f.paciente:
                print(f"   - Factura {f.id}: paciente_id={f.paciente.usuario_id}, estado={f.estado}, total=${f.monto_total}")
            else:
                print(f"   - Factura {f.id}: SIN PACIENTE, estado={f.estado}, total=${f.monto_total}")
    else:
        print(f"   ❌ NO tiene perfil_paciente")
        
        # Buscar si existe un PerfilPaciente para este usuario
        try:
            perfil_manual = PerfilPaciente.objects.get(usuario=user)
            print(f"\n   🔍 Pero SÍ existe en DB: usuario_id={perfil_manual.usuario_id}")
        except PerfilPaciente.DoesNotExist:
            print(f"\n   ❌ No existe PerfilPaciente para usuario {user.id}")
