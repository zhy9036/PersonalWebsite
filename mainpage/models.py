from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Projects(models.Model):
    user = models.ForeignKey(User)
    projectName = models.CharField(max_length=20)
    projectUrl = models.CharField(max_length=1000)
    projectToken = models.CharField(max_length=500)

    def __str__(self):
        return self.projectName

class Log(models.Model):
    project = models.ForeignKey(Projects)
    action = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
