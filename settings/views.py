from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import *
from .serializers import UserMenuSerializer,QuoteSerializer


class UserSettings(APIView):

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):

        role = request.data.get('role')
        roles = ["A","SA","C"]
        _ = {}

        if role in roles:
            _['role'] = role
        else:
            return Response({"error":"wrong role."},status=400)
        menu = UserMenu.objects.filter(**_)
        serializer = UserMenuSerializer(menu,many=True)
        return Response(serializer.data)

class QuoteView(APIView):

    def get(self, request, *args, **kwargs):
        try:
            quote = Quote.objects.get(default=True)
            data = QuoteSerializer(quote).data
        except Quote.DoesNotExist:
            data = {}
        return Response(data)
