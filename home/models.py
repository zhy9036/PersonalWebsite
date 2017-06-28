from django.db import models

# Create your models here.
class UserLoginInfo(models.Model):
    username = models.CharField(primary_key=True, max_length=20)
    password = models.CharField(max_length=20)

    def __str__(self):
        return self.username

class Projects(models.Model):
    username = models.CharField(max_length=20)
