from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """Profile model to extend User with role information."""
    ROLE_CHOICES = [
        ('operario', 'Operario'),
        ('admin', 'Administrativo'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='operario')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_operario(self):
        return self.role == 'operario'


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
        """Return a human-friendly representation: prefer tipo and lote."""
        return f"{self.tipo} - {self.lote}" if self.tipo else f"{self.lote}"

