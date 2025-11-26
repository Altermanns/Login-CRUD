from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """Profile model to extend User with role information."""
    ROLE_CHOICES = [
        ('operario', 'Operario'),
        ('preparador', 'Preparador'),
        ('admin', 'Administrativo'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='operario')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_operario(self):
        return self.role == 'operario'
    
    @property
    def is_preparador(self):
        return self.role == 'preparador'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a Profile when a User is created."""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the Profile when the User is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()


class Materia(models.Model):
    tipo = models.CharField(max_length=100, blank=True)
    cantidad = models.IntegerField(default=0)
    unidad_medida = models.CharField(max_length=50, blank=True)
    lote = models.CharField(max_length=100, blank=True)
    fecha_ingreso = models.DateField(null=True, blank=True)
    usuario_registro = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                        help_text="Usuario que registró esta materia prima")

    def __str__(self):
        """Return a more descriptive and robust string representation."""
        if self.tipo and self.lote:
            return f"{self.tipo} (Lote: {self.lote})"
        if self.tipo:
            return self.tipo
        if self.lote:
            return f"Lote: {self.lote}"
        return f"Materia ID: {self.id}"


class PreparacionMateria(models.Model):
    """Modelo para el proceso de preparación de materias primas."""
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completada', 'Completada'),
        ('rechazada', 'Rechazada'),
    ]
    
    TIPO_PROCESO_CHOICES = [
        ('limpieza', 'Limpieza'),
        ('apertura', 'Apertura'),
        ('mezclado', 'Mezclado'),
        ('ajuste_proporciones', 'Ajuste de Proporciones'),
    ]
    
    # Relación con la materia prima original
    materia_prima = models.ForeignKey(Materia, on_delete=models.CASCADE, null=True,
                                     help_text="Materia prima a procesar")
    
    # Información del proceso
    tipo_proceso = models.CharField(max_length=50, choices=TIPO_PROCESO_CHOICES,
                                   help_text="Tipo de proceso de preparación")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    
    # Cantidades y proporciones
    cantidad_procesada = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                           help_text="Cantidad procesada en kg")
    porcentaje_mezcla = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                          help_text="Porcentaje en la mezcla final (%)")
    
    # Resultado y calidad
    observaciones = models.TextField(blank=True, 
                                   help_text="Observaciones del proceso de preparación")
    calidad_resultado = models.CharField(max_length=20, choices=[
        ('excelente', 'Excelente'),
        ('buena', 'Buena'),
        ('regular', 'Regular'),
        ('deficiente', 'Deficiente'),
    ], null=True, blank=True)
    
    # Control de fechas y usuario
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    usuario_preparador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                         help_text="Usuario preparador que realizó el proceso")
    
    class Meta:
        ordering = ['-fecha_inicio']
        verbose_name = 'Preparación de Materia'
        verbose_name_plural = 'Preparaciones de Materias'
    
    def __str__(self):
        return f"{self.get_tipo_proceso_display()} de {self.materia_prima} ({self.get_estado_display()})"
    
    @property
    def duracion_proceso(self):
        """Calcula la duración del proceso si está completado."""
        if self.fecha_completado and self.fecha_inicio:
            return self.fecha_completado - self.fecha_inicio
        return None
    
    @property
    def is_completado(self):
        return self.estado == 'completada'
    
    @property
    def is_en_proceso(self):
        return self.estado == 'en_proceso'


class DetallePreparacion(models.Model):
    """Detalles específicos del proceso de preparación."""
    
    preparacion = models.ForeignKey(PreparacionMateria, on_delete=models.CASCADE,
                                   related_name='detalles')
    
    # Parámetros del proceso
    temperatura = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                    help_text="Temperatura del proceso (°C)")
    humedad = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                help_text="Humedad relativa (%)")
    tiempo_proceso = models.IntegerField(null=True, blank=True,
                                       help_text="Tiempo de proceso en minutos")
    
    # Equipos utilizados
    equipo_utilizado = models.CharField(max_length=100, blank=True,
                                      help_text="Equipo o máquina utilizada")
    
    # Resultados específicos
    rendimiento = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                    help_text="Rendimiento del proceso (%)")
    merma = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                               help_text="Porcentaje de merma (%)")
    
    # Notas adicionales
    notas_tecnicas = models.TextField(blank=True,
                                    help_text="Notas técnicas del proceso")
    
    fecha_registro = models.DateTimeField(auto_now_add=True, null=True)
    
    class Meta:
        ordering = ['-fecha_registro']
        verbose_name = 'Detalle de Preparación'
        verbose_name_plural = 'Detalles de Preparación'
    
    def __str__(self):
        return f"Detalle de {self.preparacion}"


class ProcesoHilatura(models.Model):
    """Modelo para el proceso de hilatura - transformación de fibras en hilos."""
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completada', 'Completada'),
        ('rechazada', 'Rechazada'),
    ]
    
    ETAPA_CHOICES = [
        ('cardado', 'Cardado'),
        ('peinado', 'Peinado'),
        ('hilado', 'Hilado'),
    ]
    
    # Relación con la preparación anterior
    preparacion_origen = models.ForeignKey(PreparacionMateria, on_delete=models.SET_NULL, 
                                          null=True, blank=True,
                                          help_text="Preparación de materia prima de origen")
    
    # Información del proceso
    etapa = models.CharField(max_length=20, choices=ETAPA_CHOICES,
                           help_text="Etapa del proceso de hilatura")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    
    # Cantidades
    cantidad_fibra_entrada = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                                help_text="Cantidad de fibra de entrada (kg)")
    cantidad_hilo_salida = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                              help_text="Cantidad de hilo producido (kg)")
    
    # Características del hilo
    titulo_hilo = models.CharField(max_length=50, blank=True,
                                  help_text="Título del hilo (Ne, Nm, Tex, etc.)")
    torsion = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True,
                                 help_text="Torsión del hilo (TPM - Torsiones por metro)")
    resistencia = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True,
                                     help_text="Resistencia del hilo (cN/tex)")
    
    # Resultado y calidad
    observaciones = models.TextField(blank=True,
                                   help_text="Observaciones del proceso de hilatura")
    calidad_resultado = models.CharField(max_length=20, choices=[
        ('excelente', 'Excelente'),
        ('buena', 'Buena'),
        ('regular', 'Regular'),
        ('deficiente', 'Deficiente'),
    ], null=True, blank=True)
    
    # Control de fechas y usuario
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    usuario_operador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                        help_text="Usuario operario que realizó el proceso")
    
    class Meta:
        ordering = ['-fecha_inicio']
        verbose_name = 'Proceso de Hilatura'
        verbose_name_plural = 'Procesos de Hilatura'
    
    def __str__(self):
        return f"{self.get_etapa_display()} - {self.get_estado_display()} ({self.fecha_inicio.strftime('%d/%m/%Y')})"
    
    @property
    def duracion_proceso(self):
        """Calcula la duración del proceso si está completado."""
        if self.fecha_completado and self.fecha_inicio:
            return self.fecha_completado - self.fecha_inicio
        return None
    
    @property
    def is_completado(self):
        return self.estado == 'completada'
    
    @property
    def is_en_proceso(self):
        return self.estado == 'en_proceso'
    
    @property
    def rendimiento_proceso(self):
        """Calcula el rendimiento del proceso."""
        if self.cantidad_fibra_entrada > 0:
            return (self.cantidad_hilo_salida / self.cantidad_fibra_entrada) * 100
        return 0
    
    @property
    def merma(self):
        """Calcula la merma del proceso."""
        if self.cantidad_fibra_entrada > 0:
            return ((self.cantidad_fibra_entrada - self.cantidad_hilo_salida) / self.cantidad_fibra_entrada) * 100
        return 0


class DetalleHilatura(models.Model):
    """Detalles específicos del proceso de hilatura."""
    
    hilatura = models.ForeignKey(ProcesoHilatura, on_delete=models.CASCADE,
                                related_name='detalles')
    
    # Parámetros del proceso
    velocidad_maquina = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True,
                                           help_text="Velocidad de la máquina (m/min)")
    temperatura = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                    help_text="Temperatura del proceso (°C)")
    humedad = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                help_text="Humedad relativa (%)")
    
    # Equipos y configuración
    maquina_hiladora = models.CharField(max_length=100, blank=True,
                                       help_text="Máquina hiladora utilizada")
    numero_husos = models.IntegerField(null=True, blank=True,
                                      help_text="Número de husos utilizados")
    
    # Parámetros específicos según etapa
    # Para Cardado
    velocidad_cardado = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True,
                                           help_text="Velocidad de cardado (m/min)")
    limpieza_fibras = models.CharField(max_length=20, choices=[
        ('excelente', 'Excelente'),
        ('buena', 'Buena'),
        ('regular', 'Regular'),
    ], null=True, blank=True, help_text="Nivel de limpieza de fibras (Cardado)")
    
    # Para Peinado
    longitud_fibra_eliminada = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                                  help_text="Longitud de fibra corta eliminada (mm)")
    porcentaje_impurezas_removidas = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                                        help_text="Porcentaje de impurezas removidas (%)")
    
    # Para Hilado
    grado_torsion = models.CharField(max_length=20, choices=[
        ('baja', 'Baja Torsión'),
        ('media', 'Media Torsión'),
        ('alta', 'Alta Torsión'),
    ], null=True, blank=True, help_text="Grado de torsión aplicado")
    uniformidad = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                     help_text="Uniformidad del hilo (%)")
    
    # Resultados y control de calidad
    tiempo_proceso = models.IntegerField(null=True, blank=True,
                                        help_text="Tiempo de proceso en minutos")
    defectos_encontrados = models.TextField(blank=True,
                                           help_text="Defectos encontrados durante el proceso")
    notas_tecnicas = models.TextField(blank=True,
                                     help_text="Notas técnicas del proceso")
    
    fecha_registro = models.DateTimeField(auto_now_add=True, null=True)
    
    class Meta:
        ordering = ['-fecha_registro']
        verbose_name = 'Detalle de Hilatura'
        verbose_name_plural = 'Detalles de Hilatura'
    
    def __str__(self):
        return f"Detalle de {self.hilatura}"

