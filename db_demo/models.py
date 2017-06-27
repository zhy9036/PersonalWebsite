from django.db import models

# Create your models here.
class Db_Table(models.Model):
    title = models.CharField(max_length=120)
    content = models.CharField(max_length=1000)
