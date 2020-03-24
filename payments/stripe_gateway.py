import stripe
import requests
from django.conf import settings


class Stripe:
    """
        Custom Stripe Implementation to use anywhere in project
    """

    def __init__(self, account_id=None, **kwargs):

        self.account_id = account_id
        self.kwargs = kwargs
        self.stripe = self._stripe()

    def _stripe(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        return stripe

    def oauth_link(self):
        url = f'https://connect.stripe.com/express/oauth/authorize?response_type=code&' \
            f'client_id={settings.STRIPE_CLIENT_ID}&scope=read_write'
        return url

    def connect_account(self):
        code = self.kwargs.get('code')
        if code:
            data = {
                'client_secret': settings.STRIPE_SECRET_KEY,
                'code': code,
                'grant_type': 'authorization_code'
            }

            response = requests.post('https://connect.stripe.com/oauth/token', data=data).json()

            if response.get('error'):
                self.status = False
                return {"status": False, "response": response}
            else:
                self.status = True
                return {"status": True, "response": response}
        else:
            self.status = False
            return {"status": False, "response": {"error": "Code not passed"}}

    def make_payment_intent(self):
        amount = self.kwargs.get('price')
        currency = self.kwargs.get('currency')
        payment_method = self.kwargs.get('payment_method')
        intent = self.stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            # Verify your integration in this guide by including this parameter
            metadata={'integration_check': 'accept_a_payment'},
        )
        return intent

    def make_payment_method(self, card, billing_details):
        payment_method = self.stripe.PaymentMethod.create(type="card", billing_details=billing_details, card=card)
        return payment_method

    def charge(self):

        total_amount = self.kwargs.get('total_amount', False)
        transfer_amount = self.kwargs.get('transfer_amount', False)

        assert total_amount, 'Please provide total amount.'
        assert transfer_amount, 'Please provide transfer amount.'
        assert self.account_id, "Please provide user's stripe account id."

        charge_data = {
            "payment_method_types": ['card'],
            "amount": int(total_amount),
            "currency": "usd",
            "on_behalf_of": self.account_id,
            "transfer_data": {
                "amount": int(transfer_amount),
                "destination": self.account_id,
            }
        }

        return self.stripe.PaymentIntent.create(**charge_data)
