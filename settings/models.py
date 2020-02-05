import json
from django.db import models
from .choices import *
from django.dispatch import receiver
from django.db.models.signals import post_save

class BaseModel(models.Model):
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True

class StripeSetting(models.Model):

    name = models.CharField(max_length=2,choices=stripe_setting_options,default='PF',unique=True)
    data = models.TextField()
    data_type = models.CharField(max_length=1,choices=data_types)

    def __str__(self):
        return self.get_name_display()


    def value(self):

        try:
            if self.data_type == 'S':
                return str(self.data)

            elif self.data_type == 'I':
                return int(self.data)

            elif self.data_type == 'F':
                return float(self.data)

            elif self.data_type == 'B':

                if self.data == 'True' or self.data == 'true':
                    return True

                elif self.data == 'False' or self.data == 'false':
                    return False
                else:
                    return 'Wrong Data type selected.'

            elif self.data_type == 'J':
                return json.dumps(eval(self.data))

        except:
            return 'Wrong Data type selected.'

class Menu(models.Model):

    name = models.CharField(max_length=200,unique=True)
    icon = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name

class UserMenu(models.Model):

    roles = (('A', 'Artist'), ('C', 'Collector'), ('SA', 'Admin'))

    menu = models.ForeignKey(Menu,on_delete=models.CASCADE)
    menu_url = models.CharField(max_length=200,blank=True,null=True)
    submenu = models.ForeignKey(Menu,on_delete=models.CASCADE,blank=True,null=True,related_name='submenu')
    submenu_url = models.CharField(max_length=200,blank=True,null=True)
    role = models.CharField(max_length=2,default='A',choices=roles)

    def __str__(self):
        return self.menu.name

    class Meta:
        ordering = ['menu']


    def save(self, *args,**kwargs):
        exists = UserMenu.objects.filter(menu=self.menu,submenu=self.submenu,role=self.role).exclude(id=self.id).exists()
        if not exists and self.submenu != self.menu:
            super(UserMenu, self).save(*args,**kwargs)

class Quote(BaseModel):

    quote = models.TextField()
    default = models.BooleanField(default=True)

    def __str__(self):
        return self.quote

@receiver(post_save,sender=Quote)
def updateotherquotes(sender, instance,**kwargs):
    Quote.objects.exclude(id=instance.id).update(default=False)
