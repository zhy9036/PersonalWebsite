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


class Member(models.Model):
    name = models.CharField(max_length=150, blank=False)
    jobTitle = models.CharField(max_length=150, default='World Destroyer II')
    jobDescription = models.CharField(max_length=1000, default='What does this team member to? Keep it short! This is also a great spot for social links!')
    avatar_uri = models.CharField(max_length=200, default='http://placehold.it/150x150')

    def __str__(self):
        return self.name
