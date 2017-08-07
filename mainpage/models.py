from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Project(models.Model):
    user = models.ForeignKey(User)
    projectId = models.CharField(max_length=1000)
    projectName = models.CharField(max_length=1000, blank=True)
    webUrl = models.CharField(max_length=1000, blank=True)
    sshRepoUrl = models.CharField(max_length=1000, blank=True)
    httpRepoUrl = models.CharField(max_length=1000, blank=True)
    projectToken = models.CharField(max_length=500, blank=True)
    localRepoExist = models.BooleanField(default=False)
    runnerExist = models.BooleanField(default=False)
    runnerName = models.CharField(max_length=1000, blank=True)
    localRepoPath = models.CharField(max_length=1000, blank=True)

    def __str__(self):
        return self.user.username + ' ' + self.projectName


class Log(models.Model):
    user = models.ForeignKey(User, blank=True, on_delete=models.PROTECT)
    description = models.CharField(max_length=1000, blank=True)
    projectId = models.CharField(max_length=100, blank=True)
    pipelineId = models.CharField(max_length=100, blank=True)
    logType = models.CharField(max_length=20, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        title = str(self.timestamp) + ' ' + self.description
        return title
