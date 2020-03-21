from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from arts.models import Order
from Aartcy.utils.extras import transaction_fees, unique_slug


@receiver(post_save, sender=Order)
def update_order_instance(sender, instance, **kwargs):
    pass
    # update_kwargs = {'transaction_fees':transaction_fees(instance)}
    #
    # if not instance.slug:
    #     instance.slug = unique_slug(Order,instance.product.name,True)
    #     instance.save()
    # else:
    #     Order.objects.filter(id=instance.id).update(**update_kwargs)
