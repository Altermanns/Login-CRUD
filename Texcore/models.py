from django.db import models


class Materia(models.Model):
    tipo = models.CharField(max_length=100, blank=True)
    cantidad = models.IntegerField(default=0)
    unidad_medida = models.CharField(max_length=50, blank=True)
    lote = models.CharField(max_length=100, blank=True)
    fecha_ingreso = models.DateField(null=True, blank=True)

    def __str__(self):
        """Return a human-friendly representation: prefer tipo and lote."""
        return f"{self.tipo} - {self.lote}" if self.tipo else f"{self.lote}"

