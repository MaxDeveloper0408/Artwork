from .models import *
from .models import *
from Aartcy.utils.api_response import APIResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework import viewsets, filters
from accounts.serializers import ProfileSerializer
from django.db.models import Count, Sum, Avg, Max
from .serializers import GoalSerializer, TopBuyersSerializers, \
    CertificateOfAuthenticitySerializer, PayoutSerializer, TransactionSerializer, \
    TopTagsSerializer, TopArtistSales, TopCollectors

from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet
from arts.serializers import TagSerializer, Tag
from rest_framework.pagination import LimitOffsetPagination

from payments.serializers import OrderSerializer, Order, ProductPayment
from accounts.models import Profile
from Aartcy.utils.pager import Pager, sortserialzer
from Aartcy.utils.extras import get_time, transferred_amount, chartify, \
    today, get_or_none, percentage, transaction_fees, week, \
    get_revenue, last_month

from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from Aartcy.utils import get_annotated, get_country_sales, get_aggregated

from .ga import GoogleAnalytics

from django.http import JsonResponse


class NetWorth(ViewSet):

    def list(self, request):
        data = {}
        user = request.user
        orders = Order.objects.complete().filter(product__user=user)
        data['net_revenue'] = transferred_amount(orders, flat=True)
        return Response(data)


class GoalViewSet(ModelViewSet):
    serializer_class = GoalSerializer
    http_method_names = ['get', 'post']

    def get_queryset(self):  # overiding queryset according to target_time .
        method = self.request.method

        if method == 'POST':
            return Goal.objects.filter(user=self.request.user).annotate(achieved=Sum('user__product__order__price'))
        else:
            return Goal.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        target_time = request.data.get('target_time')
        goal = request.data.get('goal')
        qs = get_or_none(Goal, user=request.user, target_time=target_time)
        if qs:
            g_obj = Goal.objects.get(id=qs.id)
            g_obj.goal = goal
            g_obj.save()
            return Response(GoalSerializer(g_obj, context={'request': request}).data)
        else:
            return super(GoalViewSet, self).create(request, *args, **kwargs)


class PouplarTags(ViewSet):

    def list(self, request):
        tags = Tag.objects.filter(product__user=request.user, ).annotate(earned=Sum('product__order__price')) \
            .annotate(sold=Count('name')).order_by('-sold').exclude(earned__isnull=True)
        data = TagSerializer(tags, many=True).data

        return Response(data)


class LatestOrders(ViewSet):

    def list(self, request):
        orders = Order.objects.complete().filter(product__user=request.user).order_by('-created_at')
        paginated_data = Pager(self.request, orders, query_params=self.request.query_params).offset_pagination()
        orders = paginated_data['results']
        serialized_data = OrderSerializer(orders, many=True).data
        paginated_data['results'] = serialized_data

        return Response(paginated_data)


class LatestCollectors(viewsets.ViewSet):
    def list(self, request):
        orders = Order.objects.all().filter(product__user=request.user).values('collector').annotate(Max('created_at')).order_by('-created_at__max')
        users = orders.values_list('collector', flat=True)
        collectors = Profile.objects.filter(user__in=users)
        serializer = ProfileSerializer(collectors[:5], many=True) # Latest 5 collectors returned
        return Response(APIResponse.success(serializer.data), status=200)


class TopBuyers(ViewSet):

    def list(self, request):
        orders = Order.objects.complete().filter(product__user=request.user)  # annotate fails directly
        collections = orders.values('email').annotate(collections=Count('email'))
        amount = orders.values('email').annotate(amount=Sum('price'))
        emails = list(collections.values_list('email', flat=True))
        buyers = Profile.objects.filter(user__email__in=emails, )  # binding collections into users profile
        # to make serialization in TopBuyersSerializers
        context = {"collections": collections, "amount": amount}
        data = TopBuyersSerializers({'buyers': buyers, }, context=context).data
        sorted_data = sortserialzer(data, 'collections', 'buyers')
        paginated_data = Pager(self.request, sorted_data, query_params=self.request.query_params).offset_pagination()
        return Response(paginated_data)


class CountMoney(ViewSet):

    def list(self, request):
        data = {}
        target = request.query_params.get('target')
        user = request.user
        orders = Order.objects.complete().filter(product__user=user, created_at__gte=get_time(target))
        data['sold'] = len(orders)
        average_price = orders.aggregate(avg=Avg('price'))['avg']
        gross_revenue = orders.aggregate(gross=Sum('price'))['gross']
        data['average_price'] = average_price if average_price else 0
        data['gross_revenue'] = gross_revenue if gross_revenue else 0
        data['net_revenue'] = transferred_amount(orders, flat=True)
        data['chart'] = chartify(orders, target)

        return Response(data)


class CollecterDashboard(ViewSet):

    def list(self, request):
        data = {}
        target = request.query_params.get('target')
        orders = Order.objects.complete().filter(email=self.request.user.email)
        collected_items = orders.aggregate(c=Count('slug'))['c']
        collected_value = orders.aggregate(s=Sum('price'))['s']
        data['collected_items'] = collected_items
        data['collected_value'] = collected_value if collected_value else 0
        data['estimated_value'] = 0
        data['chart'] = chartify(orders, target, field='spent', func='a', short_label=True)
        return Response(data)


class CertificateOfAuthenticity(ModelViewSet):
    http_method_names = ['get']
    serializer_class = CertificateOfAuthenticitySerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Order.objects.complete().filter(email=self.request.user.email)


class Payouts(ModelViewSet):
    serializer_class = PayoutSerializer

    def get_queryset(self):
        return ProductPayment.objects.filter(order__product__user=self.request.user)


class Transactions(ModelViewSet):
    http_method_names = ['get']
    serializer_class = TransactionSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return ProductPayment.objects.filter(order__product__user=self.request.user)


class Charges(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    pagination_class = LimitOffsetPagination
    pagination_class.default_limit = 10
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['product__name']
    ordering_fields = ['time', 'price', 'fees', 'net']

    def get_queryset(self):
        status = self.request.query_params.get('status')
        orders = Order.objects.filter(product__user=self.request.user)

        if status == 'all':
            orders = orders.all()
        elif status == 'pending':
            orders = orders.pending()
        elif status == 'incomplete':
            orders = orders.incomplete()
        elif status == 'refund':
            orders = orders.refund()

        return orders

    # def list(self, request):
    #     data = {}
    #     orders = Order.objects.filter(product__user=request.user)
    #     data['total_charges'] = orders.count()
    #     data['successful_charges'] = orders.complete().count()
    #     data['failed_charges'] = orders.failed().count()
    #     data['gross_sale'] = orders.complete().values_list('price').aggregate(g=Sum('price'))['g']
    #     data['processing_fees'] = transaction_fees(orders.complete(), flat=True)
    #     data['net_sales'] = transferred_amount(orders.complete(), flat=True)
    #
    #     return Response(data)


    @action(methods=['get'], detail=False)
    def order_by_status(self, request, *args, **kwargs):
        status = request.query_params.get('status')
        orders = Order.objects.filter(product__user=request.user)

        if status == 'all':
            orders = orders.all()
        elif status == 'pending':
            orders = orders.pending()
        elif status == 'incomplete':
            orders = orders.incomplete()
        elif status == 'refund':
            orders = orders.refund()

        paginated_data = Pager(self.request, orders, query_params=self.request.query_params).offset_pagination()
        orders = paginated_data['results']
        serialized_data = OrderSerializer(orders, many=True).data
        paginated_data['results'] = serialized_data

        print(paginated_data)
        return Response(paginated_data)


class AdminDashboard(ViewSet):
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Order.objects.complete()

    def list(self, request):
        return Response('Admin API')

    @action(methods=['get'], detail=False)
    def sales(self, request, *args, **kwargs):
        data = {}
        orders = self.get_queryset()
        data['total_sales'] = orders.filter(created_at=today()).count()
        all_sales = orders.count()
        data['percentage'] = percentage(data['total_sales'], all_sales)
        return Response(data)

    @action(methods=['get'], detail=False)
    def revenue(self, request, *args, **kwargs):
        data = {}
        orders = self.get_queryset()
        data['revenue'] = get_revenue(orders, created_at=today())
        total_revenue = get_revenue(orders)
        data['percentage'] = percentage(data['revenue'], total_revenue)
        return Response(data)

    @action(methods=['get'], detail=False)
    def income(self, request, *args, **kwargs):
        data = {}
        orders = self.get_queryset()
        data['income'] = transaction_fees(orders.filter(created_at=today()), flat=True)
        total_income = transaction_fees(orders, flat=True)
        data['percentage'] = percentage(data['income'], total_income)
        return Response(data)

    @action(methods=['get'], detail=False)
    def revenue_chart(self, request, *args, **kwargs):

        data = {}
        orders = self.get_queryset()
        data['week_revenue'] = get_revenue(orders, created_at__gte=week())
        data['last_month_revenue'] = get_revenue(orders, created_at__gte=last_month(1), created_at__lte=last_month())
        data['customer_reach'] = orders.distinct('email').count()
        data['week_chart'] = chartify(orders, 'W', func='a')
        return Response(data)

    @action(methods=['get'], detail=False)
    def top_cards(self, request, *args, **kwargs):
        data = {"sales": self.sales(request, *args, **kwargs).data}
        data['revenue'] = self.revenue(request, *args, **kwargs).data
        data['income'] = self.income(request, *args, **kwargs).data

        return Response(data)

    @action(methods=['get'], detail=False)
    def sales_by_country(self, request, *args, **kwargs):
        emails = self.get_queryset().values_list('email')
        profiles = Profile.objects.filter(user__email__in=emails, )
        return Response(get_country_sales(profiles, Order))

    @action(methods=['get'], detail=False)
    def new_users(self, request, *args, **kwargs):
        users = Profile.objects.all()
        today_users = users.filter(created_at=today())
        today_users_spent = self.get_queryset().filter(email__in=today_users.values_list('user__email'))
        today_users_spent = get_aggregated(today_users_spent, price='s')['price_sum']

        old_users = users.exclude(created_at=today())
        old_users_spent = self.get_queryset().filter(email__in=old_users.values_list('user__email'))
        old_users_spent = get_aggregated(old_users_spent, price='s')['price_sum']

        if today_users_spent:
            new_users_percentage = percentage(today_users_spent, today_users_spent + old_users_spent)
        else:
            new_users_percentage = 0
            today_users_spent = 0

        old_users_spent_percentage = percentage(old_users_spent, today_users_spent + old_users_spent)
        data = {
            "today_users": today_users.count(),
            "today_users_spent": today_users_spent,
            "today_users_percentage": new_users_percentage,
            "old_users": old_users.count(),
            "old_users_spent": old_users_spent,
            "old_users_percentage": old_users_spent_percentage
        }
        return Response(data)

    @action(methods=['get'], detail=False)
    def total_artist_sales(self, request, *args, **kwargs):
        orders = self.get_queryset()
        sales = get_aggregated(orders, price='s')['price_sum']
        data = {
            "total_sales": sales,
        }
        return Response(data)

    @action(methods=['get'], detail=False)
    def total_fees_collected(self, request, *args, **kwargs):
        orders = self.get_queryset()
        fees_collected = transaction_fees(orders.values_list('data', flat=True), flat=True)

        data = {
            "total_fees_collected": fees_collected,
            "total_fees_chart": chartify(orders, 'transaction_fees'),
        }
        return Response(data)

    @action(methods=['get'], detail=False)
    def top_tags(self, request, *args, **kwargs):

        orders = self.get_queryset()
        tags = get_annotated(orders, smart=True, price='s', product__tags__name='c') \
            .order_by('-price').exclude(product__tags__name=None)

        data = TopTagsSerializer(tags).data
        data = sortserialzer(data, 'value', 'top_tags', preserve_key=True)
        return Response(data)

    @action(methods=['get'], detail=False)
    def signups_today(self, request, *args, **kwargs):
        users = Profile.objects.all()
        today_users = users.filter(created_at=today())
        week_user = users.filter(created_at=week())
        data = {'today_users': today_users.count(),
                "week_user": week_user.count(),
                'users_chart': chartify(users, 'W', lookup='id', func='c')}
        return Response(data)

    @action(methods=['get'], detail=False)
    def top_artist_sales(self, request, *args, **kwargs):
        orders = self.get_queryset()
        artists = get_annotated(orders, smart=True, product__user='c', price='s')
        data = TopArtistSales(artists).data
        data = sortserialzer(data, 'earned', 'top_artists', preserve_key=True)
        return Response(data)

    @action(methods=['get'], detail=False)
    def top_collectors(self, request, *args, **kwargs):

        orders = self.get_queryset()
        collectors = get_annotated(orders, smart=True, email='c', price='s')

        data = TopCollectors(collectors).data
        data = sortserialzer(data, 'collected', 'top_collectors', preserve_key=True)
        return Response(data)

    @action(methods=['get'], detail=False)
    def top_selling_tags(self, request, *args, **kwargs):
        orders = self.get_queryset()
        tags = get_annotated(orders, smart=True, price='s', product__tags__name='c') \
            .order_by('-price').exclude(product__tags__name=None)

        data = TopTagsSerializer(tags).data
        data = sortserialzer(data, 'earnedtials, ask for offline use / use in ', 'top_tags', preserve_key=True)
        return Response(data)

    @action(methods=['get'], detail=False)
    def site_views(self, request, *args, **kwargs):
        ga = GoogleAnalytics()
        data = ga.today_site_visits()
        return Response(data)

    @action(methods=['get'], detail=False)
    def website_traffic(self, request, *args, **kwargs):
        ga = GoogleAnalytics()
        data = ga.weekly_traffic()
        return Response(data)


def testsocket(request):
    message = request.GET.get('message')
    token = request.GET.get('token')
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(f'SOCKET-{token}', {"type": "notify", "text": message})
    return JsonResponse('kfsdfh', safe=False)
