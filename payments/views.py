import json
from .stripe_gateway import Stripe
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from payments.models import PaymentMethod,ProductPayment
from arts.serializers import ProductSerializer


def oauth_link(request):
    return JsonResponse({'link':Stripe().oauth_link()})


class ConnectStripe(APIView):

    def post(self, request, *args, **kwargs):

        stripe = Stripe(**request.data)
        response = stripe.connect_account()

        if stripe.status:
            if PaymentMethod.objects.filter(user=request.user).exists():
                PaymentMethod.objects.filter(user=request.user).update(method_data=response)
            else:
                method = PaymentMethod.objects.create(user=request.user,method_data=response)
                method.save()

        return Response({"status": response['status']})


class Checkout(APIView):

    def post(self, request, *args, **kwargs):

        status = request.data.get('status')
        uid = request.data.get('uid')
        try:
            payment = ProductPayment.objects.get(uid=uid)
        except ProductPayment.DoesNotExist:
            return Response({"error": "Wrong uid."}, status=401)

        if status == True:
            payment.status = 'C'
            payment.save()
            payment.order.status = 'C'
            payment.order.save()

        else:
            payment.status = 'F'
            payment.save()
            payment.order.status = 'F'
            payment.order.save()

        return Response({"status":payment.status,"message":payment.get_status_display()})


class CheckoutViaLink(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):

        uid = kwargs.get('uid')

        try:
            payment = ProductPayment.objects.get(uid=uid)
        except ProductPayment.DoesNotExist:
            return Response({"error": "Wrong uid."}, status=401)
        try:
            response = json.loads(payment.order.data)
            if response and response['id'] == payment.payment_id:

                client_secret = response['client_secret']
                product = ProductSerializer(payment.order.product).data
                return Response({"client_secret":client_secret,"order": payment.order.slug,"product":product})

            else:
                return Response({"error": "Something went wrong."}, status=401)
        except:
           return Response({"error":"Something went wrong."}, status=401)



    def post(self, request, *args, **kwargs):

        status = request.data.get('status')
        uid = kwargs.get('uid')
        address = request.data.get('address')

        try:
            payment = ProductPayment.objects.get(uid=uid)
        except ProductPayment.DoesNotExist:
            return Response({"error": "Wrong uid."}, status=401)

        try:
            if not payment.status == 'C':

                if status == True:
                    payment.status = 'C'
                    payment.save()
                    payment.order.status = 'C'
                    payment.order.address = address
                    payment.order.save()

                else:
                    payment.status = 'F'
                    payment.save()
                    payment.order.status = 'F'
                    payment.order.address = address
                    payment.order.save()

                return Response({"status": payment.status, "message": payment.get_status_display()})
            return Response({"status": 'F', "message": 'Already Paid'})
        except Exception as e:
            return Response({'error':str(e)},status=400)


