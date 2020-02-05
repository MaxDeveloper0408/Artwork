import string,random
from django.db import models
from arts.models import Order
from django.contrib.auth.models import User

class BaseModel(models.Model):
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True

class PaymentMethod(BaseModel):

    payment_methods = (('S','Stripe'),('DT','Direct Transfer'))

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    method = models.CharField(max_length=2,choices=payment_methods,default='S')
    method_data = models.TextField(blank=True,null=True)


    def __str__(self):
        return self.get_method_display()


    def is_active(self):

        try:
            data = eval(self.method_data)
            assert data['status']
            return True
        except:
            return False

    @property
    def data(self):
        return eval(self.method_data)

    @property
    def stripe_id(self):
        if self.is_active():
            return self.data['response']['stripe_user_id']

        else:
            return None


class ProductPayment(BaseModel):

    payment_status = (('C','Complete'),('I','Incomplete'),('F','Failed'))
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    status = models.CharField(max_length=1,choices=payment_status)
    payment_id = models.CharField(max_length=200,blank=True,null=True)
    uid = models.CharField(max_length=200,blank=True,null=True)

    def __str__(self):
        return self.get_status_display()

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = generate_uid(ProductPayment)
        super(ProductPayment, self).save(*args, **kwargs)



def generate_uid(Model):

    Strings = string.ascii_uppercase + string.ascii_lowercase
    newiD = ''.join(random.choice(Strings) for object in Strings)[:42]
    while Model.objects.filter(uid=newiD).exists():
        newiD = ''.join(random.choice(Strings) for object in Strings)[:42]

    return newiD
