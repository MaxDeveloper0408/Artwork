from django.db.models import Count,Sum,Avg
from .extras import percentage
from .errors import LookupNotFound,LookupIsNotInteger

def get_country_sales(profiles,order):

    country_data = {}
    for profile in profiles:
        count = order.objects.complete().filter(email=profile.user.email).count()
        country = profile.primary_address.country
        old = country_data.get(country)
        if old:
            country_data[country] = old + count
        else:
            country_data[profile.primary_address.country] = count

    total_counts = sum(country_data.values())

    final_data = {}
    for country, c in country_data.items():
        final_data[country] = percentage(c, total_counts)

    return final_data

def values_only(queryset,lookup,s=False):
    if s:
        try:
            return sum([i[lookup] for i in queryset])
        except TypeError:
            raise LookupIsNotInteger('Look up is not integer')
    else:
        return [i[lookup] for i in queryset]

def get_annotated(queryset,smart=False,*args,**kwargs):
    f = {"s": Sum, 'c': Count, 'a': Avg}
    flat = kwargs.pop('flat',None)
    lookup = kwargs.pop('lookup',None)

    annos = {}
    if smart:
        args = []

    for k,v in kwargs.items():
        if smart:
            args.append(k)
        function = f.get(v,Count)
        name = f'{k}_{function.__name__.lower()}'
        annos[name] = function(k)

    if flat:
        _qs = queryset.values(*args).annotate(**annos)
        if not lookup:
            raise LookupNotFound('Pass lookup to return flat values')
        qs = values_only(_qs,lookup)
    else:
        qs = queryset.values(*args).annotate(**annos)

    return qs

def get_aggregated(queryset,*args,**kwargs):

    f = {"s": Sum, 'c': Count, 'a': Avg}
    annos = {}
    smart_args = []
    for k, v in kwargs.items():
        smart_args.append(k)
        function = f.get(v, Count)
        name = f'{k}_{function.__name__.lower()}'  #json key name eg: email_count
        annos[name] = function(k)

    if not args:
        args = smart_args

    qs = queryset.values(*args).aggregate(**annos)
    return qs
