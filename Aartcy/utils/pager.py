from django.conf import settings
from rest_framework.pagination import LimitOffsetPagination

class Pager:

    """
            return limit and offset if avaliable in query params
            else return settings default values
            Set default params in settings
            PAGE_LIMIT = 10
            PAGE_OFFSET = 1
        """

    def __init__(self,request,queryset,**kwargs):
        self.request = request
        self.queryset = queryset
        self.params = kwargs.get('query_params',{})

    def offset_pagination(self):

        limit = self.params.get('limit',settings.PAGE_LIMIT)
        offset = self.params.get('offset',settings.PAGE_OFFSET)
        pagination = LimitOffsetPagination()
        pagination.default_limit = limit
        pagination.offset = offset
        paginate = pagination.paginate_queryset(self.queryset, self.request)
        return pagination.get_paginated_response(paginate).data

def sortserialzer(data,sort_key,dict_key='buyers',preserve_key=False,reverse=True):
    if preserve_key:
        data = {dict_key:sorted(data[dict_key], key=lambda key: key[sort_key], reverse=reverse)}
    else:
        data = sorted(data[dict_key], key=lambda key: key[sort_key], reverse=reverse)
    return data
