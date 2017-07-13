from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Projects(models.Model):
    user = models.ForeignKey(User)
    projectId = models.CharField(max_length=1000, primary_key=True)
    projectName = models.CharField(max_length=1000)
    webUrl = models.CharField(max_length=1000)
    sshRepoUrl = models.CharField(max_length=1000)
    httpRepoUrl = models.CharField(max_length=1000)
    projectToken = models.CharField(max_length=500, blank=True)
    localRepoExist = models.BooleanField(default=False)
    localRepoPath = models.CharField(max_length=1000, blank=True)

    def __str__(self):
        return self.projectName


class Log(models.Model):
    user = models.ForeignKey(User)
    description = models.CharField(max_length=1000, blank=True)
    projectId = models.CharField(max_length=100, blank=True)
    action = models.CharField(max_length=20, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
