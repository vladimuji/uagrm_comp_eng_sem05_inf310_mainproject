from django.db import models


class Route(models.Model):
    origin_node = models.ForeignKey(
        "Node",
        on_delete=models.CASCADE,
        related_name="out_routes",
    )
    destination_node = models.ForeignKey(
        "Node",
        on_delete=models.CASCADE,
        related_name="in_routes",
    )
    distance = models.FloatField()
    locked = models.BooleanField(default=False)
    gas_cost = models.FloatField()
    cash_cost = models.FloatField()
    time = models.DurationField()
    google_json = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Route: {self.origin_node} -> {self.destination_node}"