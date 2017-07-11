from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User)
    gitlabUserId = models.CharField(max_length=500)
    screenName = models.CharField(max_length=500)
    accessToken = models.CharField(max_length=1000)
    refreshToken = models.CharField(max_length=1000)

    def __str__(self):
        return self.screenName



