from django.db import models
from .choices import COUNTRIES
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from settings.models import StripeSetting
from accounts.auth import makesecret
from settings.management.scripts import import_stripe_settings


class BaseModel(models.Model):
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True


class Profile(BaseModel):
    roles = (
        (1, 'Admin'), (2, 'Artist'), (4, 'Collector'), (6, 'Artist & Collector'), (7, 'Admin & Artist & Collector'))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profiles', default='profiles/avatar.png')
    role = models.IntegerField(choices=roles, default=2)
    phone = models.CharField(max_length=15, blank=True, null=True)
    dob = models.DateField(auto_now=False, blank=True, null=True)
    platform_fees = models.IntegerField(blank=True, null=True)
    primary_address = models.ForeignKey('Address', on_delete=models.SET_NULL, blank=True, null=True)
    credit_card = models.ForeignKey('CreditCard', on_delete=models.SET_NULL, blank=True, null=True)
    social_id = models.CharField(max_length=256, blank=True, null=True)
    social_type = models.SmallIntegerField(blank=True, null=True)
    activation_secret = models.CharField(max_length=200, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username}, {self.role}'

    def save(self, *args, **kwargs):
        if not self.platform_fees:
            try:
                obj = StripeSetting.objects.get(name='PF')
                self.platform_fees = obj.value()

            except StripeSetting.DoesNotExist:
                import_stripe_settings()  # if setting does not exist create one.
                obj = StripeSetting.objects.get(name='PF')
                self.platform_fees = obj.value()

        return super(Profile, self).save(*args, **kwargs)

    @property
    def update_secret(self, *args, **kwargs):
        self.activation_secret = makesecret(self.user.username)
        self.save(*args, **kwargs)
        return self.activation_secret


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except:
        Profile.objects.create(user=instance).save()


class Address(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.CharField(max_length=200)
    zip_code = models.CharField(max_length=9)
    state = models.CharField(max_length=200)
    country = models.CharField(max_length=2, choices=COUNTRIES, default='IN')
    address_line1 = models.TextField()
    address_line2 = models.TextField(default='', blank=True, null=True)

    def __str__(self):
        return self.country


class CreditCard(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    number = models.CharField(max_length=19)
    exp_month = models.CharField(max_length=2)
    exp_year = models.CharField(max_length=4)
    cvc = models.CharField(max_length=3)
