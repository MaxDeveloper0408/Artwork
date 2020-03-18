from .serializers import *
from django.conf import settings
from rest_framework import viewsets
from accounts.auth import secretMessage
from rest_framework.views import APIView
from payments.stripe_gateway import Stripe
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status, permissions
from .forms import ProductPaymentForm,OrderForm
from accounts.mailers import send_buy_link
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import LimitOffsetPagination,PageNumberPagination
import re


class ProductViewSet(viewsets.ModelViewSet):

    serializer_class = ProductSerializer
    pagination_class = LimitOffsetPagination
    pagination_class.default_limit = 10

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)

    def perform_create(self, serializer):

        categories = self.request.data.get('category')
        tags = self.request.data.get('tags')
        categories = self.valid_list(categories,'category')
        tags = self.valid_list(tags)
        kwargs = {}

        if categories:
            kwargs['category'] = categories

        if tags:
            _ = []
            for tag in tags:
                try:
                    t = Tag.objects.create(name=tag)
                    t.save()
                    _.append(t.id)
                except:
                    t = Tag.objects.get(name=tag)
                    _.append(t.id)

            kwargs['tags'] = _

        try:
            serializer.save(**kwargs).save()
        except :
            raise ValidationError(detail={'all': ["Wrong Data"]})


    def perform_update(self, serializer):
        kwargs = {}
        categories = self.request.data.get('category')
        tags = self.request.data.get('tags')
        tags = self.valid_list(tags)

        if not self.kwargs.get('method', None) == 'partial':


            categories = self.valid_list(categories, 'category')

            if categories:
                kwargs['category'] = categories
        else:
            categories = self.valid_list(categories,)

            if categories:
                kwargs['category'] = categories

        if tags:
            _ = []
            for tag in tags:
                try:
                    t = Tag.objects.create(name=tag)
                    t.save()
                    _.append(t.id)

                except:
                    t = Tag.objects.get(name=tag)
                    _.append(t.id)

            kwargs['tags'] = _

        serializer.save(**kwargs)


    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        self.kwargs['method'] = 'partial'
        return self.update(request, *args, **kwargs)


    def valid_list(self ,form_data,field=None):
        try:
            l =form_data.split(',')
            valid_list = []
            for i,_ in enumerate(l):
                _ = _.strip()
                if str(_).isnumeric() or  str(_).isalpha():
                    valid_list.append(_.lower())

            if len(valid_list) == 0:
                if field:
                    raise ValidationError(detail={field: ["This field is required"]})
                else:
                    return False
            else :
                return valid_list
        except:
            if field:
                raise ValidationError(detail={field: ["This field is required"]})
            else:
                return False

    # @permission_classes([permissions.AllowAny])
    @action(detail=True,methods=['post'])
    def buy(self,request, *args, **kwargs):

        link = request.GET.get('link')
        id = kwargs.get('pk')
        address = request.data.get('address')
        if address:
            email = address.get('email')
        else:
            return  Response({ "address": "Not found." })

        # just to make product available for any user
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response({ "detail": "Not found." })

        stripe = Stripe()

        artist = product.user
        artist_payment_mthd = artist.paymentmethod_set.first()

        order_data = {"email": email, "product": product.id,
                      "price": product.price, "address": address}

        if link == 'true':
            order_data['by'] = 'L'

        order_form = OrderForm(order_data)

        if order_form.is_valid():
            o = order_form.save(commit=False)
        else:
            return Response({"error": order_form.errors.get_json_data()}, status=400)

        if artist_payment_mthd and artist_payment_mthd.is_active():
            stripe_user_id = artist_payment_mthd.stripe_id
        else:
            return Response({"error": "Stripe account not connected."}, status=400)

        price = product.price * 100 #converting into cents.
        stripe.account_id = stripe_user_id
        stripe.kwargs["total_amount"] = price
        stripe.kwargs["transfer_amount"] = price * artist.profile.platform_fees /100

        try:
            response = stripe.charge()
        except Exception as e:
            return Response({"error": str(e)},status=400)

        o.data = response
        o.save()
        client_secret = response['client_secret']

        stripe_payment_id = response['id']
        payment_data = {"order": o.id, "status": "I", "payment_id": stripe_payment_id}
        payment_form = ProductPaymentForm(payment_data)

        if payment_form.is_valid():
            p = payment_form.save(commit=False)
            p.save()
        else:
            return Response({"error":payment_form.errors.get_json_data()},status=400)

        if not link == 'true':
            return Response({"client_secret":client_secret,"order": o.slug,"uid":p.uid})

        else:
            url = f'{settings.DOMAIN}/{product.user.username}/{product.slug}/{p.uid}/'
            return Response({"link": url})


    @action(detail=False, methods=['post'])
    def emaillink(self,request,*args,**kwargs):
        link = request.data.get('link')
        email = request.data.get('email')
        # user_id = request.data.get('user_id')
        # product_id = request.data.get('product_id')
        # amount = request.data.get('amount')
        # tags = request.data.get('tags')
        # message = request.data.get('message')

        if not link:
            return Response({'status': 'error', 'message': 'Link should not be empty.'}, status=400)

        if not email:
            return Response({'status': 'error', 'message': 'Email should not be empty.'}, status=400)

        try:
            if send_buy_link(email, 'Arttwork Buy Product', link):
                return Response({'status': 'success'})
            else:
                return Response({'status': 'error', 'message': 'Sending email failed.'}, status=405)
        except:
            return Response({'status': 'error', 'message': 'Exception occurred.'}, status=406)

    @action(detail=False, methods=['get'])
    def search(self,request,*args,**kwargs):
        query = self.request.query_params.get('q')
        if query:
            products = self.get_queryset().filter(name__icontains=query)
            serializer = self.get_serializer(products,many=True)
            return Response(serializer.data)
        return Response('Please provide search query.')


class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer




