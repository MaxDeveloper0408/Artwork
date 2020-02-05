from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True


class Notifications(BaseModel):

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    message = models.TextField()
    sent = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    image = models.ImageField(default='assets/notify.png')

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Notifications'
