from datetime import datetime, timedelta
from django.db.models import Count,Sum,Avg
import json
import string,random
from django.utils.text import slugify


WEEK  = "W"
MONTH = "M"
YEAR  = "Y"

TIME_TARGETS = [WEEK,MONTH,YEAR]

time_ = {
        WEEK: datetime.today() - timedelta(days=7),
        MONTH: datetime.today() - timedelta(days=28),
        YEAR: datetime.today() - timedelta(days=365),
    }

time_inc = {
    WEEK: timedelta(days=1),
    MONTH: timedelta(days=7),
    YEAR: timedelta(days=30),
}


def valid_target(target):
    if target in TIME_TARGETS:
        return target
    else:
        return YEAR

def get_time(key):
    key = valid_target(key)
    return time_.get(key)

def smart_date(date,target):
    target = valid_target(target)
    return date + time_inc.get(target),date + time_inc.get(target)

def chartify(data,target,lookup='price',field='value',func='s',short_label=False):

    target = valid_target(target)
    f = {"s":Sum,'c':Count,'a':Avg}
    function = f.get(func,f.get('s'))
    chart_data = []
    date = get_time(target).date()
    current_date = datetime.now().date()

    while date != current_date:

        d = data.filter(created_at__gte=date,created_at__lte=smart_date(date,target)[1])
        if target == 'Y':
            if short_label:
                label = date.strftime("%b %y") # Jun 19
            else:
                label = date.strftime("%B %Y") # June 2019
            earning = d.aggregate(total=function(lookup))['total']

        elif target == 'M':
            label = date.strftime("%A %d-%b-%Y") # Sunday 09-Jun-2019
            earning = d.aggregate(total=function(lookup))['total']

        elif target == 'W':
            label = date.strftime("%A") # Sunday
            earning = d.aggregate(total=function(lookup))['total']

        else:
            break

        earned = earning if earning else 0 # if aggregation return None

        chart_data.append({"label": label, field: earned})

        date = smart_date(date,target)[0]

        if date > current_date:
            break

    return chart_data

def stats(data,lookup='price',field='earned',func='s'):

    stats_data= []

    return stats_data

def cents_to_usd(cents):
    return int(cents / 100)


def transferred_amount(queryset,flat=False,key=False):
    if not flat:
        try:
            if key:
                data = json.loads(queryset['data'])
            else:
                data = json.loads(queryset.data)
            total_amount = data['amount']
            transction_fees = data['transfer_data']['amount']
            return cents_to_usd(total_amount) - cents_to_usd(transction_fees)
        except:
            return 0
    else:
        final_flat = []
        for i in queryset:
            try:
                i = json.loads(i.data)
                total_amount = i['amount']
                transction_fees = i['transfer_data']['amount']
                final_flat.append(cents_to_usd(total_amount) - cents_to_usd(transction_fees))
            except:
                print(i)
        return sum(final_flat)

def transaction_fees(queryset,flat=False,key=False):

    if not flat:

        try:
            if key:
                data = json.loads(queryset['data'])
            else:
                data = json.loads(queryset.data)

            fees = data['transfer_data']['amount']
            return cents_to_usd(fees)
        except:
            return 0
    else:
        final_flat = []
        for i in queryset:
            try:
                i = json.loads(i.data)
                fees = i['transfer_data']['amount']
                final_flat.append(cents_to_usd(fees))
            except:
                pass
        return sum(final_flat)

def payable_account(data,key=False):
    try:
        if key:
            data = json.loads(data['data'])
        else:
            data = json.loads(data.data)
        accnt = data['on_behalf_of']

        return 'X'*8 + '-'+ accnt[-5:]
    except:
        return 0

def amount_charged(data,key=False):
    try:
        if key:
            data = json.loads(data['data'])
        else:
            data = json.loads(data.data)
        return cents_to_usd(data['amount'])
    except:
        return 0

def get_or_none(model, *args, **kwargs):
    key = kwargs.get('key',False)

    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return key
    except:
        return key

def get_or_none_serializer(model,serializer, *args, **kwargs):
    key = kwargs.get('key',None)

    try:
        return serializer(model.objects.get(*args, **kwargs)).data
    except model.DoesNotExist:
        return key

def delta(_date,days=1,opr='M',d=True):
    if opr == 'M':
       _d = _date - timedelta(days=days)
    else:
        _d = _date + timedelta(days=days)

    if d:
        return _d.date()
    else:
        return _d

def today():
    return datetime.today()

def week():
    return datetime.today() - timedelta(days=7)

def month():
    return datetime.today() - timedelta(days=30)

def this_month(day=1):
    return today().replace(day=day)

def last_month(day=None):
    first = today().replace(day=1)
    month = first - timedelta(days=1)
    if day:
        month = month.replace(day=day)
    return month

def date():
    return datetime

def percentage(_is,of,r=2):
    if of == 0:
        return 0
    try:
        val = _is/of
        return round(val*100,r)
    except:
        return 0

def get_revenue(queryset,lookup='price',**kwargs):
    if kwargs:
        data = queryset.filter(**kwargs).values(lookup).aggregate(r=Sum(lookup))['r']
    else:
        data = queryset.values(lookup).aggregate(r=Sum(lookup))['r']

    return data if data else 0


def unique_slug(Model, name, r=False):
    """
        Create & return unique slug

    """

    Strings = string.ascii_uppercase + string.ascii_lowercase

    if r:
        newiD = ''.join(random.choice(Strings) for object in Strings)[:5]
        while Model.objects.filter(slug=newiD).exists():
            newiD = slugify(''.join(random.choice(Strings) for object in Strings)[:5])
    else:
        newiD = slugify(name)
        while Model.objects.filter(slug=newiD).exists():
            newiD = slugify(name) + slugify(''.join(random.choice(Strings) for object in Strings)[:5])

    return newiD
