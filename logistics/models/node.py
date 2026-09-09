from django.db import models


class Node(models.Model):
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    listed = models.BooleanField(default=True)

    def __str__(self):
        return self.name