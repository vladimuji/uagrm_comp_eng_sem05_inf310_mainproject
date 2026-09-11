from django.db import models


class Node(models.Model):
    id = models.IntegerField(primary_key=True)  # SQL doesn't use AUTO_INCREMENT semantics you may want; adjust if needed
    city_name = models.CharField(max_length=100, db_column="city_name")
    state = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    listed = models.BooleanField(default=True)

    class Meta:
        db_table = "nodes"
        managed = False  # <- IMPORTANT, see note below

    def __str__(self):
        return self.name