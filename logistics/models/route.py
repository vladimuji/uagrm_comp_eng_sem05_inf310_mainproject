from django.db import models


class Route(models.Model):
    nodo_origen = models.ForeignKey(
        "Node",
        on_delete=models.CASCADE,
        related_name="rutas_salientes",
    )
    nodo_destino = models.ForeignKey(
        "Node",
        on_delete=models.CASCADE,
        related_name="rutas_entrantes",
    )
    distancia = models.FloatField()
    bloqueado = models.BooleanField(default=False)
    costo_gasolina = models.FloatField()
    costo_monetario = models.FloatField()
    tiempo = models.DurationField()
    google_json = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Route: {self.nodo_origen} -> {self.nodo_destino}"