from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class UserLoginInfo(models.Model):
    username = models.CharField(primary_key=True, max_length=20)
    password = models.CharField(max_length=20)

    def __str__(self):
        return self.username

class Projects(models.Model):
    user = models.ForeignKey(User)
    projectName = models.CharField(max_length=20)
    projectUrl = models.CharField(primary_key=True, max_length=1000)
    projectToken = models.CharField(max_length=500)

    def __str__(self):
        return self.projectName

class UserPerf(models.Model):
    username = models.ForeignKey(User)