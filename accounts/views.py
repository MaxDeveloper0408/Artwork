from . import auth
from .mailers import *
from .serializers import *
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .forms import SignupForm,AuthenticationForm
from django.contrib.auth.forms import SetPasswordForm
from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from payments.models import PaymentMethod

class Signup(viewsets.ViewSet):

    permission_classes = (AllowAny,)
    http_method_names = ['post',]

    def create(self, request, *args, **kwargs):

        form_data = {
                'username':request.data.get('username').lower(),
                'password1':request.data.get('password'),
                'password2':request.data.get('confirm_password'),
                'email':request.data.get('email'),
                'role':request.data.get('role'),
                }

        valid_roles = ['A','C']

        form = SignupForm(form_data)
        messages = form.errors.get_json_data()

        if form.is_valid():
            if form_data['role'] in valid_roles:
                obj = form.save()
                activation_secret = auth.makesecret(form_data['username'])

                Profile.objects.filter(user_id=obj.id).update(role=form_data['role'],
                                           activation_secret=activation_secret)


                token = auth.makeJWT(form_data['username'],activation_secret)
                method = PaymentMethod.objects.filter(user_id=obj.id).first()
                if method:
                    is_stripe_connected = True
                else:
                    is_stripe_connected = False

                SendEmail(form_data['email'],EMAIL_ACTIVATION_SUB,token)
                token, created = Token.objects.get_or_create(user=obj)
                data = {'status': True, 'token': token.key,
                        "verified":obj.profile.is_verified,"is_profile_complete":False,
                        'is_stripe_connected':is_stripe_connected}

                return Response(data)
            else:
                messages['role'] = 'Please enter a valid role.'
        else:
            if messages.get('password2'):
                messages['password'] = messages.get('password2')
                messages.pop('password2')
                if messages.get('password1'):
                    messages.pop('password1')

        return Response({"status":False,"errors":messages},status=400)


class Login(viewsets.ViewSet):
    permission_classes = (AllowAny,)
    http_method_names = ['post', ]

    def create(self, request, *args, **kwargs):
        email = request.data.get('email').lower()
        print(email)

        try:
            user = User.objects.get(email=email)
            form_data = {'username':user.username,'password':request.data.get('password')}

        except User.DoesNotExist:

            err = {"errors": [{"message":"User does not exist", "code": "und"}]}
            return Response(err,status=400)

        form  = AuthenticationForm(data=form_data)

        if form.is_valid():
            user = form.get_user()
            token, created = Token.objects.get_or_create(user=user)

            is_profile_complete = False
            if user.first_name and user.last_name and user.profile.primary_address:
                is_profile_complete  = True

            method = PaymentMethod.objects.filter(user=user).first()
            if method and method.is_active():
                is_stripe_connected = True
            else:
                is_stripe_connected = False

            data = {'token': token.key,"verified":user.profile.is_verified,
                    "is_profile_complete":is_profile_complete,'is_stripe_connected':is_stripe_connected}
            return Response(data)

        else:

            err = {"errors":[]}
            for error in form.errors.get_json_data().values():
                err['errors'].extend(error)

        return Response(err,status=400)


class ForgotPassword(viewsets.ViewSet):
    permission_classes = (AllowAny,)
    http_method_names = ['post', ]

    def create(self, request, *args, **kwargs):
        username = request.data.get("username")
        email = request.data.get("email")
        error = None
        user = None

        if username:
            try:
                user = User.objects.get(username=username)
            except:
                error = 'Username does not exist.'

        elif email:
            try:
                user = User.objects.get(email=email)
            except:
                error = 'Email does not exist.'

        else:
            error = 'Please enter username or email.'

        if user:
            secret = user.profile.update_secret
            token = auth.makeJWT(user.username,secret)
            SendEmail(user.email, 'Forgot Password', token,activation=False)
            return Response({'message':'Please check your email.'})


        return Response({'error':error},status=401)


class ResetPassword(APIView):
    permission_classes = (AllowAny,)


    def get(self, request, *args, **kwargs):

        secret  = kwargs.get('secret')
        data = auth.checkJWT(secret)
        if data:
            username = data['username']
            key = data['key']
            try:
                user = User.objects.get(username=username)
                if user.profile.activation_secret == key:
                    return Response({'valid':True})
            except:
                pass

        return Response({'valid': False},status=400)

    def post(self, request, *args, **kwargs):

        secret = kwargs.get('secret')
        data = auth.checkJWT(secret)
        password = request.data.get('password')

        if data:
            username = data['username']
            key = data['key']

            try:
                user = User.objects.get(username=username)
            except:
                user = None

            if user.profile.activation_secret == key:

                form_data = {"new_password1": password, "new_password2": password}
                change_password_form = SetPasswordForm(user, form_data)

                if change_password_form.is_valid():
                    change_password_form.save()
                    user.profile.update_secret  # update activation secret
                    message = {"status": True}
                    return JsonResponse(message)

                else:
                    message = change_password_form.errors.get_json_data()
                    message['status'] = False
                    if message.get('new_password1'):
                        message['password'] = message.pop('new_password1')
                    message['confirm_password'] = message.pop('new_password2')

                message['valid'] = True
                return JsonResponse(message,status=401)

        return JsonResponse({'valid': False}, status=401)


class ProfileViewSet(viewsets.ViewSet):

    http_method_names = ['get','put']

    def list(self, request):
        queryset = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(queryset)
        return Response(serializer.data)

    @action(['PUT'],False)
    def update_profile(self, request, *args, **kwargs):

        mutable_data = request.data
        username = mutable_data.pop('username',False)
        password = mutable_data.pop('password',False)
        primary_address = request.data.get('primary_address')

        if username:
            raise ValidationError(detail={"username": ["Username cannot be changed."]})
        if password:
            raise ValidationError(detail={"password": ["Use Password api end point to change password."]})

        u_serializer = UserSerializer(request.user,data=mutable_data,partial=True)
        u_serializer.is_valid(raise_exception=True)
        u_serializer.save()

        p_instance = Profile.objects.get(user=request.user)
        p_serializer = ProfileSerializer(p_instance,data=mutable_data,partial=True)
        p_serializer.is_valid(raise_exception=True)

        if primary_address:
            try:
                address = Address.objects.get(id=primary_address)
                if address.user.username == request.user.username:
                    p_serializer.save(primary_address=address)
                else:
                    raise ValidationError(detail={"primary_address": ["Address does not belong to you."]})
            except Address.DoesNotExist as e:
                raise ValidationError(detail={"primary_address": [str(e)]})

        else:
            p_serializer.save()
        return Response(p_serializer.data)

    @action(['PUT'], False)
    def change_password(self, request, *args, **kwargs):
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        form_data = {"new_password1":password,"new_password2":confirm_password}
        change_password_form = SetPasswordForm(request.user,form_data)
        if change_password_form.is_valid():
            change_password_form.save()
            message = {"status": True}
            return Response(message)
        else:
            message = change_password_form.errors.get_json_data()
            message['status'] = False
            if message.get('new_password1'):
                message['password'] = message.pop('new_password1')
            message['confirm_password'] = message.pop('new_password2')

            return Response(message,status=401)

    @action(['PUT'], False)
    def updateimage(self,request, *args, **kwargs):
        image = {'image': request.FILES.get('image')}
        p_instance = Profile.objects.get(user=request.user)
        serializer  = ProfileImageSerializer(p_instance,data=image,partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)


def activate(request,secret):
    """
    Activate user Profile

    Models and views are using in this View :

    1 if jwt and extract data is equalto fasle
        * Renders HTML Template ( accounts/invalid_signup.htm )

    2 if jwt and extract data is equalto fasle
        * HttpResponse ( Activated )

    1 Models:
      * Profile : :model:`accounts.Profile`


    """
    # activate user  Profile
    #check jwt and extract data
    data = auth.checkJWT(secret)
    if data:
        #if data is available
        #get usrname from data
        user = User.objects.get(username=data['username'])
        #get profile object of user
        AccountObj = Profile.objects.get(user=user)

        #if key matches to token
        if AccountObj.activation_secret == data['key']:
            #create another token
            AccountObj.activation_secret  = auth.makesecret()
            AccountObj.is_verified  = True
            user.save()
            AccountObj.save()

            return HttpResponse('Activated')

        return render(request, 'accounts/invalid_signup.html')
    else:
        return render(request, 'accounts/invalid_signup.html')








