from django.db import models
from django.contrib.auth.models import User
from Aartcy.utils import unique_slug


class BaseModel(models.Model):
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='categories', blank=True, null=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Category, self.name)
            super(Category, self).save(*args, **kwargs)
        else:
            super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'


class Tag(BaseModel):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, blank=False, null=True)

    def __str__(self):
        return self.name


class Product(BaseModel):
    type_choices = ((0, 'Digital'), (1, 'Physical'))
    status_choices = (('L', 'Live'), ('T', 'Test'), ('D', 'Disabled'))
    currency_choices = (('usd', 'USD'), ('eur', 'EUR'))

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    currency = models.CharField(max_length=3, choices=currency_choices, default='usd')
    price = models.FloatField(default=0)
    description = models.TextField(default='', blank=True, null=True)
    type = models.SmallIntegerField(choices=type_choices, default=1)
    image = models.ImageField(upload_to='products', default='profiles/avatar.png')
    attachment = models.FileField(upload_to='uploads/', null=True, blank=True)
    status = models.CharField(max_length=1, choices=status_choices, default='L')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Artist')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    length = models.FloatField(default=0)
    width = models.FloatField(default=0)
    height = models.FloatField(default=0)
    weight = models.FloatField(default=0)
    notes = models.TextField(blank=True, null=True)
    link = models.URLField()
    deleted = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.name


class OrderQuerySet(models.QuerySet):
    def complete(self):
        return self.filter(status='C')

    def incomplete(self):
        return self.filter(status='I')

    def failed(self):
        return self.filter(status='F')

    def pending(self):
        return self.filter(status='P')

    def refund(self):
        return self.filter(status='R')


class Order(BaseModel):
    order_status = (('C', 'Complete'), ('I', 'Incomplete'), ('P', 'Pending'), ('F', 'Failed'), ('R', 'Refund'), ('D', 'Chargebacks'))
    by_options = (('O', 'On Site'), ('L', 'By Email Link'),)
    currency_options = (('usd', 'USD'), ('eur', 'EUR'))

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    currency = models.CharField(max_length=3, choices=currency_options, default='usd')
    price = models.FloatField(default=0)
    fees = models.FloatField(default=0, blank=True)
    net = models.FloatField(default=0, blank=True)
    collector = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Collector')
    tags = models.ManyToManyField(Tag, blank=True)
    by = models.CharField(max_length=1, choices=by_options, default='O')
    status = models.CharField(max_length=1, choices=order_status, default='I', blank=True)
    time = models.DateTimeField(blank=True)
    payment_intent_id = models.CharField(max_length=32, blank=True)

    objects = OrderQuerySet.as_manager()

    def __str__(self):
        return self.product.name
