from rest_framework.serializers import Serializer
from rest_framework.exceptions import APIException
from accounts.serializers import ProfileSerializer, Profile, ProfileSerializerReadOnly, Address
from Aartcy.utils import Logger
from .models import *
from django.db.models import Count, Sum, Avg
from payments.serializers import *
from Aartcy.utils.extras import transaction_fees, \
    payable_account as pa, amount_charged as ac, transferred_amount, \
    get_or_none_serializer, get_time, percentage


def get_profile(**kwargs):
    try:
        return Profile.objects.get(**kwargs)
    except Profile.DoesNotExist:
        return None


class GoalSerializer(ModelSerializer):
    achieved = SerializerMethodField('get_achieved')

    class Meta:
        model = Goal
        fields = ['id', 'goal', 'target_time', 'achieved', 'user']

    def get_achieved(self, obj):
        user = self.context['request'].user
        target = self.context['request'].data.get('target_time')
        amount = Order.objects.complete().filter(product__user=user, created_at__gte=get_time(target)) \
            .aggregate(gross=Sum('price'))['gross']
        return amount

    def to_internal_value(self, data):
        mutable_dict = data.copy()
        mutable_dict['user'] = self.context['request'].user.id
        return super(GoalSerializer, self).to_internal_value(mutable_dict)


class BuyerSerializer(ProfileSerializer):
    collections = SerializerMethodField('get_coll')
    amount = SerializerMethodField('get_amount')
    city = SerializerMethodField('get_city')
    phone = SerializerMethodField('get_amount')

    class Meta:
        model = Profile
        fields = ['username', 'email', 'first_name', 'last_name', 'collections', 'amount', 'city', 'phone']

    def get_coll(self, profile):  # adds collections to matched email
        for c in self.context['collections']:
            if profile.user.email == c['email']:
                return c['collections']
        return 0

    def get_amount(self, profile):
        for c in self.context['amount']:
            if profile.user.email == c['email']:
                return c['amount']
        return 0

    def get_city(self, profile):
        for c in self.context['amount']:
            if profile.user.email == c['email']:
                return self.primary_address_attrs(profile, 'city')

    def get_phone(self, profile):
        for c in self.context['amount']:
            if profile.user.email == c['email']:
                return self.primary_address_attrs(profile, 'phone')

    def primary_address_attrs(self, profile, field):  # return address field if primary address is available
        if profile.primary_address:
            return getattr(profile.primary_address, field)
        else:
            return None


class TopBuyersSerializers(Serializer):
    buyers = BuyerSerializer(many=True)


class CertificateOfAuthenticitySerializer(OrderSerializer):
    collected_on = SerializerMethodField('get_collected')
    artwork_by = SerializerMethodField('get_artwork_by')

    class Meta:
        model = Order
        fields = ['collected_on', 'price', 'artwork_by', 'product']

    def get_collected(self, obj):
        return obj.created_at

    def get_artwork_by(self, obj):
        return ProfileSerializerReadOnly(obj.product.user.profile).data


class PayoutSerializer(ModelSerializer):
    requested_on = SerializerMethodField('get_requested_on')
    transaction_id = SerializerMethodField('get_transaction_id')
    amount = SerializerMethodField('get_amount')
    fees_chaged = SerializerMethodField('get_fees_chaged')
    payable_account = SerializerMethodField('get_payable_account')
    status = SerializerMethodField('get_status')

    class Meta:
        model = ProductPayment
        fields = ['requested_on', 'transaction_id', 'amount',
                  'fees_chaged', 'payable_account', 'status']

    def get_requested_on(self, obj):
        return obj.created_at

    def get_transaction_id(self, obj):
        return obj.uid

    def get_amount(self, obj):
        return obj.order.price

    def get_fees_chaged(self, obj):
        return transaction_fees(obj.order)

    def get_payable_account(self, obj):
        return pa(obj.order)

    def get_status(self, obj):
        return obj.status


class TransactionSerializer(ModelSerializer):
    product = SerializerMethodField('get_product')
    order_id = SerializerMethodField('get_order_id')
    time = SerializerMethodField('get_time')
    amount_charged = SerializerMethodField('get_amount_charged')
    fees = SerializerMethodField('get_fees')
    net_revenue = SerializerMethodField('get_revenue')
    collector = SerializerMethodField('get_collector')

    class Meta:
        model = ProductPayment
        fields = ['order_id', 'fees', 'net_revenue', 'time', 'amount_charged', 'status', 'collector', 'product']

    def get_product(self, obj):
        return ProductSerializer(obj.order.product).data

    def get_order_id(self, obj):
        return obj.order.slug

    def get_time(self, obj):
        return obj.created_at

    def get_amount_charged(self, obj):
        return ac(obj.order)

    def get_fees(self, obj):
        return transaction_fees(obj.order)

    def get_revenue(self, obj):
        return transferred_amount(obj.order)

    def get_collector(self, obj):
        return get_or_none_serializer(Profile, ProfileSerializer, user__email=obj.order.email)


class TopTagsSerializer(Serializer):
    top_tags = SerializerMethodField('get_top_tags')

    def get_top_tags(self, obj):
        tags = []
        for a in obj:
            data = {'name': a['product__tags__name'], 'earned': a['price_sum'],
                    'value': a['product__tags__name_count']}
            tags.append(data)

        return tags


class TopArtistSales(Serializer):
    top_artists = SerializerMethodField('get_top_artists')

    def get_top_artists(self, obj):
        artists = []
        for a in obj:
            profile = ProfileSerializer(get_profile(user__id=a['product__user'])).data
            if profile:
                data = {'user': profile, 'sales': a['product__user_count'], 'earned': a['price_sum']}
                artists.append(data)
        return artists


class TopCollectors(Serializer):
    top_collectors = SerializerMethodField('get_top_collectors')

    def get_top_collectors(self, obj):
        collectors = []
        for a in obj:

            profile = ProfileSerializer(get_profile(user__email=a['email'])).data
            if profile:
                data = {'user': profile, 'collected': a['email_count'], 'spent': a['price_sum']}
                collectors.append(data)
        return collectors
