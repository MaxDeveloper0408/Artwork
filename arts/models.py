from django.db import models
from django.contrib.auth.models import User
from Aartcy.utils import unique_slug

class BaseModel(models.Model):
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True


class Category(BaseModel):

    name  = models.CharField(max_length=200)
    image = models.ImageField(upload_to='categories',blank=True,null=True)
    slug  = models.SlugField(unique=True,blank=True,null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Category,self.name)
            super(Category, self).save(*args, **kwargs)
        else:
            super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'


class Tag(BaseModel):
    name = models.CharField(max_length=200,unique=True)

    def __str__(self):
        return self.name


    def save(self, *args,**kwargs):
        self.name = str(self.name).lower().strip()
        super(Tag,self).save(*args,**kwargs)


class Product(BaseModel):

    user = models.ForeignKey(User,on_delete=models.CASCADE,verbose_name='Artist')
    name = models.CharField(max_length=200)
    price = models.FloatField()
    description = models.TextField()
    category = models.ManyToManyField(Category)
    slug = models.SlugField(unique=True, blank=True, null=True)
    image = models.ImageField(upload_to='products', blank=True, null=True)
    status_choices = (('I','Inactive'),('A','Active'))
    status = models.CharField(max_length=1,choices=status_choices,default='I')
    tags = models.ManyToManyField(Tag)


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Product,self.name)
            super(Product, self).save(*args, **kwargs)
        else:
            super(Product, self).save(*args, **kwargs)


class OrderQuerySet(models.QuerySet):
    def complete(self):
        return self.filter(status='C')

    def incomplete(self):
        return self.filter(status='I')

    def failed(self):
        return self.filter(status='F')


class Order(BaseModel):

    order_status = (('C','Complete'),('I','Incomplete'),('F','Failed'))
    by_options = (('O','On Site'),('L','By Email Link'),)
    email = models.EmailField()
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    status = models.CharField(max_length=1,choices=order_status,default='I')
    data = models.TextField(blank=True,null=True)
    price = models.IntegerField()
    slug = models.SlugField(unique=True,blank=True,null=True)
    address = models.TextField(default='{}')
    by = models.CharField(max_length=1,choices=by_options,default='O')
    transaction_fees = models.IntegerField(default=0)
    objects = OrderQuerySet.as_manager()

    def __str__(self):
        return self.product.name





