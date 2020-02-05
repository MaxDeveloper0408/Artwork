from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from payments.models import ProductPayment
from notifications.generator import NotificationGenerator


@receiver(post_save, sender=ProductPayment)
def update_order_instance(sender, instance, **kwargs):
    user = instance.order.product.user
    product = instance.order.product
    email = instance.order.email
    kwargs = {"user":user,"product":product,'status':instance.status,'uid':instance.uid,'email':email}
    generator = NotificationGenerator(**kwargs)
    generator.payment_status_notification()
