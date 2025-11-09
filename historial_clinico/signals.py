# historial_clinico/signals.py

"""
Signals para automatizar la conexión entre Episodios y Planes de Tratamiento.

Este módulo implementa el MODELO HÍBRIDO:
- Si un episodio NO está vinculado a un plan → funciona como episodio simple
- Si un episodio SÍ está vinculado a un plan → actualiza automáticamente el progreso del plan
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import EpisodioAtencion


@receiver(post_save, sender=EpisodioAtencion)
def actualizar_plan_tratamiento_al_guardar_episodio(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta cada vez que se guarda un EpisodioAtencion.
    
    Flujo:
    1. Verifica si el episodio está vinculado a un ItemPlanTratamiento
    2. Si SÍ:
       - Actualiza el estado del ítem de PENDIENTE → EN_PROGRESO
       - Actualiza el estado del plan general
       - Registra fecha_realizada cuando el ítem se marca como completado
    3. Si NO:
       - No hace nada (episodio simple independiente)
    
    Argumentos:
        sender: La clase del modelo (EpisodioAtencion)
        instance: La instancia específica del episodio que se guardó
        created: True si es un nuevo episodio, False si es una actualización
        **kwargs: Argumentos adicionales
    """
    
    # Verificar si este episodio está vinculado a un ítem del plan
    if not instance.item_plan_tratamiento:
        # Es un episodio simple (independiente) - no hacer nada
        return
    
    # Este episodio SÍ está vinculado a un plan de tratamiento
    item_plan = instance.item_plan_tratamiento
    plan = item_plan.plan
    
    # ============================================================================
    # PASO 1: Actualizar estado del ItemPlanTratamiento
    # ============================================================================
    
    if created:
        # Es el primer episodio vinculado a este ítem
        print(f"📋 Nuevo episodio vinculado al ítem: {item_plan.servicio.nombre}")
        
        # Si el ítem estaba PENDIENTE, pasarlo a EN_PROGRESO
        if item_plan.estado == 'PENDIENTE':
            item_plan.estado = 'EN_PROGRESO'
            item_plan.save(update_fields=['estado'])
            print(f"   ✅ Ítem actualizado: PENDIENTE → EN_PROGRESO")
    
    # ============================================================================
    # PASO 2: Verificar si el ítem debe marcarse como COMPLETADO
    # ============================================================================
    
    # Por ahora, asumimos que UN episodio = ítem completado
    # (A futuro puedes agregar un campo "marcar_como_completado" en el episodio)
    
    # Si el ítem ya está COMPLETADO, no hacer nada más
    if item_plan.estado == 'COMPLETADO':
        return
    
    # Si hay un campo especial en el episodio que indica "completar ítem"
    # o si quieres marcar manualmente, puedes agregar lógica aquí
    # Por ahora, dejamos que el odontólogo marque manualmente desde el admin o API
    
    # ============================================================================
    # PASO 3: Actualizar el estado general del PlanDeTratamiento
    # ============================================================================
    
    # Llamar al método que recalcula el progreso del plan
    plan.actualizar_progreso()
    
    print(f"   📊 Plan actualizado: {plan.titulo}")
    print(f"   📈 Progreso: {plan.porcentaje_completado}%")


@receiver(post_save, sender='tratamientos.ItemPlanTratamiento')
def actualizar_plan_al_cambiar_item(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta cuando se actualiza el estado de un ItemPlanTratamiento.
    
    Esto maneja los casos donde el odontólogo marca manualmente un ítem como COMPLETADO
    desde el admin o desde la API (sin pasar por un episodio).
    
    Flujo:
    1. Si el ítem cambió a COMPLETADO → Actualizar plan
    2. Recalcular porcentaje de progreso
    3. Si todos los ítems están completados → Marcar plan como COMPLETADO
    """
    
    if not created:
        # Es una actualización (no creación)
        plan = instance.plan
        
        # Si el ítem fue marcado como COMPLETADO y no tiene fecha_realizada
        if instance.estado == 'COMPLETADO' and not instance.fecha_realizada:
            instance.fecha_realizada = timezone.now()
            instance.save(update_fields=['fecha_realizada'])
        
        # Actualizar progreso del plan
        plan.actualizar_progreso()


# ============================================================================
# FUNCIONALIDAD ADICIONAL: Auto-completar ítems después de N episodios
# ============================================================================

def verificar_auto_completar_item(item_plan):
    """
    Lógica opcional para auto-completar un ítem después de cierto número de episodios.
    
    Ejemplo de uso:
    - Una "Endodoncia" requiere 3 sesiones
    - Después del 3er episodio, auto-completar el ítem
    
    Esta función NO está conectada a los signals por defecto.
    Puedes llamarla manualmente si quieres implementar esta funcionalidad.
    """
    
    # Contar episodios asociados a este ítem
    total_episodios = item_plan.episodios_asociados.count()
    
    # Lógica de ejemplo: Si hay 3+ episodios, completar
    # (Esto lo puedes hacer más sofisticado con un campo "sesiones_requeridas" en el servicio)
    if total_episodios >= 3 and item_plan.estado != 'COMPLETADO':
        item_plan.estado = 'COMPLETADO'
        item_plan.fecha_realizada = timezone.now()
        item_plan.save()
        return True
    
    return False
