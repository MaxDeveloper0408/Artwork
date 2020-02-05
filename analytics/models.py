from django.db import models
from django.contrib.auth.models import User

class BaseModel(models.Model):
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True


class Goal(BaseModel):

    time_choices = (('M','Monthly'),('W','Weekly'),('Y','Yearly'))
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    goal = models.IntegerField()
    target_time = models.CharField(max_length=1,choices=time_choices)

    def __str__(self):
        return f'{self.user.username} : {self.goal}'


