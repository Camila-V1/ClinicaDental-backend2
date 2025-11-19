from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
import uuid
from usuarios.models import PerfilPaciente, PerfilOdontologo
from tratamientos.models import Servicio, PlanDeTratamiento, ItemPlanTratamiento, CategoriaServicio


class Command(BaseCommand):
    help = 'Poblar planes propuestos para paciente María'

    def handle(self, *args, **options):
        # Ejecutar en el contexto del tenant
        with schema_context('clinica_demo'):
            self.poblar_planes()

    def poblar_planes(self):
        self.stdout.write("=" * 80)
        self.stdout.write("🦷 POBLANDO PLANES PROPUESTOS PARA MARÍA")
        self.stdout.write("=" * 80)
        
        # Crear categoría si no existe
        categoria, created = CategoriaServicio.objects.get_or_create(
            nombre='Odontología General',
            defaults={'descripcion': 'Servicios generales de odontología', 'orden': 1}
        )
        if created:
            self.stdout.write(f"✅ Categoría creada: {categoria.nombre}")
        
        # Buscar paciente María
        try:
            paciente = PerfilPaciente.objects.get(usuario__email='paciente1@test.com')
            self.stdout.write(f"✅ Paciente: {paciente.usuario.nombre} {paciente.usuario.apellido} (ID: {paciente.pk})")
        except PerfilPaciente.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ No se encontró paciente María"))
            return
        
        # Buscar odontólogo
        try:
            odontologo = PerfilOdontologo.objects.first()
            self.stdout.write(f"✅ Odontólogo: Dr. {odontologo.usuario.nombre} {odontologo.usuario.apellido} (ID: {odontologo.pk})")
        except:
            self.stdout.write(self.style.ERROR("❌ No se encontró odontólogo"))
            return
        
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("📋 CREANDO PLANES PROPUESTOS")
        self.stdout.write("=" * 80)
        
        # PLAN 1: Ortodoncia
        self.stdout.write("\n1️⃣ Creando Plan: Ortodoncia Completa...")
        plan1 = PlanDeTratamiento.objects.create(
            paciente=paciente,
            odontologo=odontologo,
            titulo="Ortodoncia Completa con Brackets Metálicos",
            descripcion="Plan de tratamiento ortodóncico completo con brackets metálicos de alta calidad. Duración estimada: 18 meses. Incluye consultas mensuales de ajuste y seguimiento post-tratamiento.",
            estado='PROPUESTO',
            prioridad='ALTA',
            fecha_presentacion=timezone.now(),
        )
        
        items_ortodoncia = [
            {"nombre": "Consulta de Ortodoncia", "precio": "150.00", "orden": 1, "notas": "Evaluación completa con radiografías panorámicas"},
            {"nombre": "Limpieza Dental Profunda", "precio": "100.00", "orden": 2, "notas": "Limpieza profunda requerida antes de colocar brackets"},
            {"nombre": "Colocación de Brackets", "precio": "1200.00", "orden": 3, "notas": "Brackets metálicos de alta calidad, incluye primer arco"},
            {"nombre": "Controles Mensuales", "precio": "1200.00", "orden": 4, "notas": "12 controles mensuales incluidos, ajuste de arcos"},
            {"nombre": "Retiro de Brackets", "precio": "200.00", "orden": 5, "notas": "Retiro cuidadoso de brackets y limpieza final"},
            {"nombre": "Retenedores", "precio": "450.00", "orden": 6, "notas": "Retenedores superior e inferior, uso permanente"},
            {"nombre": "Radiografía Final", "precio": "80.00", "orden": 7, "notas": "Radiografía para verificar resultados finales"},
        ]
        
        total = Decimal('0.00')
        for item_data in items_ortodoncia:
            servicio, _ = Servicio.objects.get_or_create(
                nombre=item_data["nombre"],
                defaults={
                    'codigo_servicio': f'{item_data["nombre"][:6].upper()}{uuid.uuid4().hex[:4].upper()}',
                    'descripcion': item_data["notas"],
                    'precio_base': Decimal(item_data["precio"]),
                    'tiempo_estimado': 60,
                    'categoria': categoria
                }
            )
            
            ItemPlanTratamiento.objects.create(
                plan=plan1,
                servicio=servicio,
                precio_servicio_snapshot=Decimal(item_data["precio"]),
                estado='PENDIENTE',
                orden=item_data["orden"],
                notas=item_data["notas"]
            )
            total += Decimal(item_data["precio"])
        
        self.stdout.write(f"   ✅ Plan creado (ID: {plan1.id}) - Total: ${total}")
        
        # PLAN 2: Implante
        self.stdout.write("\n2️⃣ Creando Plan: Implante Dental...")
        plan2 = PlanDeTratamiento.objects.create(
            paciente=paciente,
            odontologo=odontologo,
            titulo="Implante Dental Pieza 26",
            descripcion="Colocación de implante dental de titanio en pieza 26 con corona de porcelana. Incluye cirugía, osteointegración y corona definitiva.",
            estado='PROPUESTO',
            prioridad='MEDIA',
            fecha_presentacion=timezone.now() - timedelta(days=1),
        )
        
        items_implante = [
            {"nombre": "Consulta de Implantología", "precio": "100.00", "orden": 1, "notas": "Evaluación con radiografías 3D"},
            {"nombre": "Cirugía de Implante", "precio": "800.00", "orden": 2, "notas": "Implante de titanio de alta calidad"},
            {"nombre": "Corona de Porcelana", "precio": "700.00", "orden": 3, "notas": "Corona de porcelana-cerámica sobre implante"},
            {"nombre": "Control Final", "precio": "50.00", "orden": 4, "notas": "Control con radiografía para verificar ajuste"},
        ]
        
        total = Decimal('0.00')
        for item_data in items_implante:
            servicio, _ = Servicio.objects.get_or_create(
                nombre=item_data["nombre"],
                defaults={
                    'codigo_servicio': f'{item_data["nombre"][:6].upper()}{uuid.uuid4().hex[:4].upper()}',
                    'descripcion': item_data["notas"],
                    'precio_base': Decimal(item_data["precio"]),
                    'tiempo_estimado': 90,
                    'categoria': categoria
                }
            )
            
            ItemPlanTratamiento.objects.create(
                plan=plan2,
                servicio=servicio,
                precio_servicio_snapshot=Decimal(item_data["precio"]),
                estado='PENDIENTE',
                orden=item_data["orden"],
                notas=item_data["notas"]
            )
            total += Decimal(item_data["precio"])
        
        self.stdout.write(f"   ✅ Plan creado (ID: {plan2.id}) - Total: ${total}")
        
        # PLAN 3: Blanqueamiento
        self.stdout.write("\n3️⃣ Creando Plan: Blanqueamiento Dental...")
        plan3 = PlanDeTratamiento.objects.create(
            paciente=paciente,
            odontologo=odontologo,
            titulo="Blanqueamiento Dental Profesional",
            descripcion="Tratamiento de blanqueamiento dental profesional con técnica combinada (en consultorio + domiciliaria). Incluye limpieza previa y kit para casa.",
            estado='PROPUESTO',
            prioridad='BAJA',
            fecha_presentacion=timezone.now() - timedelta(days=2),
        )
        
        items_blanqueamiento = [
            {"nombre": "Limpieza Dental", "precio": "80.00", "orden": 1, "notas": "Limpieza profesional necesaria antes del blanqueamiento"},
            {"nombre": "Blanqueamiento en Consultorio", "precio": "300.00", "orden": 2, "notas": "Aplicación de gel blanqueador con luz LED"},
            {"nombre": "Kit Blanqueamiento Domiciliario", "precio": "150.00", "orden": 3, "notas": "Cubetas personalizadas y gel para 2 semanas"},
            {"nombre": "Control y Retoque", "precio": "50.00", "orden": 4, "notas": "Control a las 2 semanas con retoque si es necesario"},
        ]
        
        total = Decimal('0.00')
        for item_data in items_blanqueamiento:
            servicio, _ = Servicio.objects.get_or_create(
                nombre=item_data["nombre"],
                defaults={
                    'codigo_servicio': f'{item_data["nombre"][:6].upper()}{uuid.uuid4().hex[:4].upper()}',
                    'descripcion': item_data["notas"],
                    'precio_base': Decimal(item_data["precio"]),
                    'tiempo_estimado': 60,
                    'categoria': categoria
                }
            )
            
            ItemPlanTratamiento.objects.create(
                plan=plan3,
                servicio=servicio,
                precio_servicio_snapshot=Decimal(item_data["precio"]),
                estado='PENDIENTE',
                orden=item_data["orden"],
                notas=item_data["notas"]
            )
            total += Decimal(item_data["precio"])
        
        self.stdout.write(f"   ✅ Plan creado (ID: {plan3.id}) - Total: ${total}")
        
        # Resumen
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("✅ RESUMEN")
        self.stdout.write("=" * 80)
        
        planes = PlanDeTratamiento.objects.filter(paciente=paciente, estado='PROPUESTO')
        self.stdout.write(f"\n📋 Total planes propuestos: {planes.count()}")
        for plan in planes:
            items_count = plan.items.count()
            self.stdout.write(f"  • {plan.titulo} - {items_count} items - Prioridad: {plan.get_prioridad_display()}")
        
        self.stdout.write("\n🎉 PROCESO COMPLETADO")
        self.stdout.write("\n💡 Accede al frontend como paciente1@test.com")
        self.stdout.write("   Ir a 'Solicitudes de Tratamiento'\n")



