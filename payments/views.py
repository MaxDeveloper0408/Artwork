import json
import stripe
from .stripe_gateway import Stripe
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from payments.models import PaymentMethod, ProductPayment
from arts.serializers import ProductSerializer
from Aartcy.utils.api_response import APIResponse
from accounts.forms import *
from accounts import auth
from accounts.mailers import *
from arts.models import *
from arts.forms import *


def oauth_link(request):
    return JsonResponse({'link': Stripe().oauth_link()})


class CurrentBalance(APIView):

    def get(self, request, *args, **kwargs):
        stripe = Stripe()
        payment_method = PaymentMethod.objects.filter(user=request.user).first()

        if payment_method and payment_method.is_active():
            stripe_user_id = payment_method.stripe_id
        else:
            return Response({"error": "Stripe account not connected."}, status=400)

        stripe.account_id = stripe_user_id
        balance = stripe.balance()

        if not balance:
            return Response({"error": "Could not get balance of account."}, status=400)

        return Response({'status': 'success', 'balance': balance.available[0]})


class ConnectStripe(APIView):

    def post(self, request, *args, **kwargs):

        stripe = Stripe(**request.data)
        response = stripe.connect_account()

        if stripe.status:
            if PaymentMethod.objects.filter(user=request.user).exists():
                PaymentMethod.objects.filter(user=request.user).update(method_data=response)
            else:
                method = PaymentMethod.objects.create(user=request.user, method_data=response)
                method.save()

        return Response({"status": response['status']})


class SavePayment(APIView):
    def post(self, request):
        return Response(APIResponse.success('Saved payment result'))


class PaymentIntent(APIView):
    def post(self, request, *args, **kwargs):
        payment_info = request.data
        print(payment_info)
        product_slug = payment_info.get('product')
        try:
            product = Product.objects.get(slug=product_slug)
            artist = product.user
            artist_payment_method = artist.paymentmethod_set.first()
            if not artist_payment_method:
                return Response(APIResponse.error(
                    message='Your stripe account is not connected. Please connect your account and try again',
                    code=-3000), status=401)

            artist_stripe_id = artist_payment_method.stripe_id
            if not artist_stripe_id:
                return Response(APIResponse.error(message='Your stripe account is not valid', code=-3000), status=401)

        except Product.DoesNotExist:
            return Response(APIResponse.error(message='The product does not exist', code=-3001), status=404)

        email = payment_info.get('email')
        signup_data = {
            'username': payment_info.get('name').lower(),
            'password1': 'initial password',
            'password2': 'initial password',
            'email': email,
        }
        address_data = {
            'city': payment_info.get('city'),
            # 'zip_code': payment_info.get('postCode'),
            'zip_code': ' ',
            'state': payment_info.get('state'),
            'country': payment_info.get('country'),
            'address_line1': payment_info.get('addressLine1'),
            'address_line2': payment_info.get('addressLine2'),
        }

        activation_secret = auth.makesecret(payment_info.get('name').lower())
        profile_data = {
            'role': 4,
            'phone': payment_info.get('phone'),
            'dob': payment_info.get('dob'),
            'activation_secret': activation_secret,
        }
        credit_card_data = {
            'number': payment_info.get('creditCardNumber'),
            'exp_month': payment_info.get('exp_month'),
            'exp_year': payment_info.get('exp_year'),
            'cvc': payment_info.get('cvc'),
        }
        order_data = {
            'currency': payment_info.get('currency'),
            'price': payment_info.get('price'),
            'by': payment_info.get('by')
        }

        order_form = OrderForm(order_data)

        try:
            collector = User.objects.get(email=email)
        except User.DoesNotExist:
            # create a collector account

            signup_form = SignupForm(signup_data)
            address_form = AddressForm(data=address_data)
            credit_card_form = CreditCardForm(data=credit_card_data)
            profile_form = ProfileForm(data=profile_data)

            if not signup_form.is_valid():
                print(signup_form.errors.get_json_data())
                return Response(APIResponse.error(message='Invalid collector information', code=-3003), status=201)

            if not address_form.is_valid():
                print(address_form.errors.get_json_data())
                return Response(APIResponse.error(message='Invalid address information', code=-3002), status=201)

            if not credit_card_form.is_valid():
                print(credit_card_form.errors.get_json_data())
                return Response(APIResponse.error(message='Invalid credit card information', code=-3002),
                                status=201)

            if not profile_form.is_valid():
                print(profile_form.errors.get_json_data())
                return Response(APIResponse.error(message='Invalid profile information', code=-3002), status=201)

            if not order_form.is_valid():
                print(order_form.errors.get_json_data())
                return Response(APIResponse.error('Invalid order information', code=-3002), status=201)

            collector = signup_form.save()  # at this point, the relation table(OneToOne, OneToMany Models created)

            address = address_form.save(commit=False)
            address.user = collector
            address.save()

            credit_card = credit_card_form.save(commit=False)
            credit_card.user = collector
            credit_card.save()

            profile_form = ProfileForm(data=profile_data, instance=collector.profile)
            profile = profile_form.save(commit=False)
            profile.primary_address = address
            profile.credit_card = credit_card
            profile.user = collector
            profile.save()
            if send_registration_notification(email) is False:
                return Response(APIResponse.error(
                    message='An error occurred while sending registration notification email to the collector',
                    code=-3002), status=500)

        tag_list = []
        for iterator in payment_info.get('tags'):
            query_set = Tag.objects.filter(slug=iterator.get('slug'))
            if len(query_set) == 0:  # exist the tag in Tags table
                tag = Tag.objects.create(name=iterator.get('name'), slug=iterator.get('slug'))
            else:
                tag = query_set[0]
            tag_list.append(tag)

        print('Tag List', tag_list)

        order = order_form.save(commit=False)
        order.product = product
        order.collector = collector
        order.save()
        order.tags.set(tag_list)

        stripe_manager = Stripe(artist_stripe_id)
        billing_detail = {'address': {
            'city': payment_info.get('city'),
            'country': payment_info.get('country'),
            'line1': payment_info.get('addressLine1'),
            'line2': payment_info.get('addressLine2'),
            'postal_code': '',
            'state': payment_info.get('state'),
        }}
        try:
            method = stripe_manager.make_payment_method(credit_card_data, billing_detail)
            stripe_manager.kwargs["price"] = int(payment_info['price'] * 100)
            stripe_manager.kwargs["currency"] = payment_info['currency']
            stripe_manager.kwargs["application_fee"] = payment_info['price'] * artist.profile.platform_fees
            stripe_manager.kwargs["payment_method"] = method.id
            intent = stripe_manager.make_payment_intent()
            order.payment_intent_id = intent.id
            order.save()
        except stripe.error.StripeError as e:
            print('Stripe error', e.error.message)
            return Response(APIResponse.error(message=e.error.message, code=-3008),
                            status=400)

        return Response(APIResponse.success({
            'paymentIntent': intent,
            'paymentMethod': method
        }))


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
                return Response({"client_secret": client_secret, "order": payment.order.slug, "product": product})

            else:
                return Response({"error": "Something went wrong."}, status=401)
        except:
            return Response({"error": "Something went wrong."}, status=401)

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
            return Response({'error': str(e)}, status=400)
