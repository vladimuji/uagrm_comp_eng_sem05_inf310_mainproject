from django.db import models


class Route(models.Model):
    origin_node = models.ForeignKey(
        "Node", on_delete=models.CASCADE, related_name="out_routes",
        db_column="origin_node",
    )
    destination_node = models.ForeignKey(
        "Node", on_delete=models.CASCADE, related_name="in_routes",
        db_column="destination_node",
    )
    range_km = models.FloatField()
    locked_road = models.BooleanField(default=False)
    gas_cost = models.FloatField()
    cash_cost = models.FloatField()
    time_lapse = models.DurationField()
    google_json = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "edges"
        managed = False  # same note
        unique_together = (("origin_node", "destination_node"),)

    def __str__(self):
        return f"Route: {self.origin_node} -> {self.destination_node}"