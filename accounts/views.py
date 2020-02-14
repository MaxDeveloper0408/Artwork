from . import auth
from .mailers import *
from .serializers import *
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .forms import SignupForm, AuthenticationForm
from django.contrib.auth.forms import SetPasswordForm
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from payments.models import PaymentMethod
from google.oauth2 import id_token
from google.auth.transport import requests
import facebook
from django.conf import settings
from requests_oauthlib import OAuth1Session

resource_owner_key = ''
resource_owner_secret = ''


class Signup(viewsets.ViewSet):
    permission_classes = (AllowAny,)
    http_method_names = ['post', ]

    def create(self, request, *args, **kwargs):

        form_data = {
            'username': request.data.get('username').lower(),
            'password1': request.data.get('password'),
            'password2': request.data.get('confirm_password'),
            'email': request.data.get('email'),
            'role': request.data.get('role'),
        }

        valid_roles = ['A', 'C']

        form = SignupForm(form_data)
        messages = form.errors.get_json_data()

        if form.is_valid():
            if form_data['role'] in valid_roles:
                activation_secret = auth.makesecret(form_data['username'])
                token = auth.make_jwt(form_data['username'], activation_secret)

                if send_email(form_data['email'], EMAIL_ACTIVATION_SUB, token) is True:
                    obj = form.save()

                    Profile.objects.filter(user_id=obj.id).update(role=form_data['role'],
                                                                  activation_secret=activation_secret)

                    is_stripe_connected = False
                    # method = PaymentMethod.objects.filter(user_id=obj.id).first()
                    # if method:
                    #     is_stripe_connected = True
                    # else:
                    #     is_stripe_connected = False

                    token, created = Token.objects.get_or_create(user=obj)
                    data = {'status': 'success', 'data': {'token': token.key,
                                                          "verified": obj.profile.is_verified,
                                                          "is_profile_complete": False,
                                                          'is_stripe_connected': is_stripe_connected}}

                    return Response(data)
                else:
                    try:
                        messages['email'].append({'message': 'could not send activation email.'})
                    except:
                        messages['email'] = [{'message': 'could not send activation email.'}]
            else:
                try:
                    messages['role'].append({'message': 'Please enter a valid role.'})
                except:
                    messages['role'] = [{'message': 'Please enter a valid role.'}]
        else:
            if messages.get('password2'):
                messages['password'] = messages.get('password2')
                messages.pop('password2')
                if messages.get('password1'):
                    messages.pop('password1')

        return Response({"status": "error", "errors": messages}, status=400)


class Login(viewsets.ViewSet):
    permission_classes = (AllowAny,)
    http_method_names = ['post', ]

    LOGIN_WITH_EMAIL = 0
    LOGIN_WITH_FACEBOOK = 1
    LOGIN_WITH_TWITTER = 2
    LOGIN_WITH_GOOGLE = 3

    def create(self, request, *args, **kwargs):
        global resource_owner_key
        global resource_owner_secret

        email = ''
        login_type = request.data.get('type')
        if login_type != self.LOGIN_WITH_TWITTER:
            email = request.data.get('email').lower()

        # verify google idToken in the case of social login
        if login_type == self.LOGIN_WITH_GOOGLE:
            print('Login with google account')
            google_request = requests.Request()
            token = request.data.get('idToken')
            try:
                id_info = id_token.verify_oauth2_token(token,
                                                       google_request,
                                                       settings.GOOGLE_CLIENT_ID)
            except ValueError:
                result = {'status': 'error', 'message': 'Invalid google user', 'code': -1001}
                return Response(result, status=401)

            if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                result = {'status': 'error', 'message': 'Invalid google issuer', 'code': -1001}
                return Response(result, status=401)
            social_id = request.data.get('id')

        # verify facebook access token and id
        if login_type == self.LOGIN_WITH_FACEBOOK:
            print('Login with facebook account')
            token = request.data.get('authToken')

            try:
                graph = facebook.GraphAPI(access_token=token)
                user_info = graph.get_object(id='me', fields='id')
                print(user_info)
                social_id = request.data.get('id')
                if social_id != user_info.get('id'):
                    result = {'status': 'error', 'message': 'Invalid facebook issuer', 'code': -1001}
                    return Response(result, status=401)
            except facebook.GraphAPIError:
                result = {'status': 'error', 'message': 'Invalid facebook user', 'code': -1001}
                return Response(result, status=401)

        # get id from twitter user's credential
        if login_type == self.LOGIN_WITH_TWITTER:
            print('login with twitter account')
            token = request.data.get('token')
            # might be needed to check if token is equal to the resource_owner_key of login_url()
            verifier = request.data.get('verifier')
            client_key = settings.TWITTER_CONSUMER_API_KEY
            client_secret = settings.TWITTER_CONSUMER_API_SEC_KEY
            access_token_url = 'https://api.twitter.com/oauth/access_token'
            oauth = OAuth1Session(client_key,
                                  client_secret=client_secret,
                                  resource_owner_key=resource_owner_key,
                                  resource_owner_secret=resource_owner_secret,
                                  verifier=verifier)
            oauth_tokens = oauth.fetch_access_token(access_token_url)
            resource_owner_key = oauth_tokens.get('oauth_token')
            resource_owner_secret = oauth_tokens.get('oauth_token_secret')
            # get access user profile
            credential_url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
            oauth = OAuth1Session(client_key,
                                  client_secret=client_secret,
                                  resource_owner_key=resource_owner_key,
                                  resource_owner_secret=resource_owner_secret)
            params = {'include_email': 'true'}
            credential = oauth.get(credential_url, params=params).json()
            social_id = credential['id']
            if social_id is None or social_id == '':
                return Response({'status': 'error', 'message': 'Invalid twitter user', 'code': -1001})

        # check if the user exists, for login user via email, find the user by email
        # for social login user, find the user by social_id
        try:
            if login_type == self.LOGIN_WITH_EMAIL:
                user = User.objects.get(email=email)
                form_data = {'username': user.username, 'password': request.data.get('password')}
            else:
                profiles = Profile.objects.filter(social_id=social_id, social_type=login_type).values('user_id')
                if profiles.count() != 1:
                    # redirect signup page
                    result = {'status': 'error', 'message': 'Social user should complete their profile',
                              'data': {'social-id': social_id, 'social-type': login_type}, 'code': -1003}
                    return Response(result, status=401)
                else:
                    user_id = profiles[0]['user_id']
                    user = User.objects.get(pk=user_id)

        except User.DoesNotExist:
            # if login is not via social, return error
            if login_type == self.LOGIN_WITH_EMAIL:
                result = {'status': 'error', 'message': 'User does not exist', 'code': -1002}
                return Response(result, status=401)

        # check password
        if login_type == self.LOGIN_WITH_EMAIL:
            form = AuthenticationForm(data=form_data)
            if form.is_valid():
                user = form.get_user()
            else:
                result = {'status': 'error', 'message': 'Invalid email or password', 'code': -1004}
                return Response(result, status=401)

        token, created = Token.objects.get_or_create(user=user)
        is_profile_complete = False
        if user.first_name and user.last_name and user.profile.primary_address:
            is_profile_complete = True

        method = PaymentMethod.objects.filter(user=user).first()
        if method and method.is_active():
            is_stripe_connected = True
        else:
            is_stripe_connected = False

        # profile = Profile.objects.filter(user=user).values('role')
        # if profile:
        #     # Artist
        #     if profile[0]['role'] == 'A':
        #         if is_profile_complete is False:
        #             result = {'status': 'error', 'message': 'Artist should complete their profile', 'code': -1006}
        #             return Response(result, status=401)
        #         if is_stripe_connected is False:
        #             result = {'status': 'error', 'message': 'Artist should be verified their stripe payment method',
        #                       'code': -1007}
        #             return Response(result, status=401)
        #     else:  # collector
        #         if is_profile_complete is False:
        #             result = {'status': 'error', 'message': 'Collector should complete their profile', 'code': -1006}
        #             return Response(result, status=401)

        result = {'status': 'success', 'data': {'token': token.key, 'verified': user.profile.is_verified,
                                                'is_profile_complete': is_profile_complete,
                                                'is_stripe_connected': is_stripe_connected}}
        return Response(result)


# get twitter authentication page url
@api_view()
@permission_classes([AllowAny])
def twitter_login_url(request):
    global resource_owner_key
    global resource_owner_secret

    request_token_url = 'https://api.twitter.com/oauth/request_token'
    client_key = settings.TWITTER_CONSUMER_API_KEY
    client_secret = settings.TWITTER_CONSUMER_API_SEC_KEY
    oauth = OAuth1Session(client_key, client_secret=client_secret)
    fetch_response = oauth.fetch_request_token(request_token_url)
    resource_owner_key = fetch_response.get('oauth_token')
    resource_owner_secret = fetch_response.get('oauth_token_secret')
    print('oauth_token:', resource_owner_key)
    print('oauth_token_secret:', resource_owner_secret)
    base_authorization_url = 'https://api.twitter.com/oauth/authorize'
    authorization_url = oauth.authorization_url(base_authorization_url)

    return Response({'status': 'success', 'data': {'url': authorization_url}})


class ForgotPassword(viewsets.ViewSet):
    permission_classes = (AllowAny,)
    http_method_names = ['post', ]

    def create(self, request, *args, **kwargs):
        # username = request.data.get("username")
        email = request.data.get("email")
        error = None
        user = None

        if email:
            try:
                user = User.objects.get(email=email)
            except:
                error = 'Email does not exist.'

        else:
            error = 'Please enter email.'

        if user:
            secret = user.profile.update_secret
            token = auth.make_jwt(user.username, secret)

            if send_email(user.email, 'Forgot Password', token, activation=False) is True:
                return Response({'message': 'Please check your email.'})
            else:
                error = 'Invalid email.'

        return Response({'error': error}, status=401)


class ResetPassword(viewsets.ViewSet):
    permission_classes = (AllowAny,)
    http_method_names = ['post', ]

    def create(self, request, *args, **kwargs):

        token = request.data.get('token')
        data = auth.check_jwt(token)
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
                return JsonResponse(message, status=401)

        return JsonResponse({'valid': False}, status=401)


class ProfileViewSet(viewsets.ViewSet):
    http_method_names = ['get', 'put']

    def list(self, request):
        queryset = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(queryset)
        return Response(serializer.data)

    @action(['PUT'], False)
    def update_profile(self, request, *args, **kwargs):
        mutable_data = request.data
        username = mutable_data.pop('username', False)
        password = mutable_data.pop('password', False)
        primary_address = request.data.get('primary_address')

        if username:
            raise ValidationError(detail={"username": ["Username cannot be changed."]})
        if password:
            raise ValidationError(detail={"password": ["Use Password api end point to change password."]})

        u_serializer = UserSerializer(request.user, data=mutable_data, partial=True)
        u_serializer.is_valid(raise_exception=True)
        u_serializer.save()

        p_instance = Profile.objects.get(user=request.user)
        p_serializer = ProfileSerializer(p_instance, data=mutable_data, partial=True)
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
            address = Address.objects.create(user=request.user)
            address.save()
            a_serializer = AddressSerializer(address, data=mutable_data, partial=True)
            a_serializer.is_valid(raise_exception=True)
            a_serializer.save()
            p_serializer.save(primary_address=address)

        return Response(p_serializer.data)

    @action(['PUT'], False)
    def change_password(self, request, *args, **kwargs):
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        form_data = {"new_password1": password, "new_password2": confirm_password}
        change_password_form = SetPasswordForm(request.user, form_data)
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

            return Response(message, status=401)

    @action(['PUT'], False)
    def updateimage(self, request, *args, **kwargs):
        image = {'image': request.FILES.get('image')}
        p_instance = Profile.objects.get(user=request.user)
        serializer = ProfileImageSerializer(p_instance, data=image, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)


def activate(request, secret):
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
    # check jwt and extract data
    data = auth.check_jwt(secret)
    if data:
        # if data is available
        # get usrname from data
        user = User.objects.get(username=data['username'])
        # get profile object of user
        AccountObj = Profile.objects.get(user=user)

        # if key matches to token
        if AccountObj.activation_secret == data['key']:
            # create another token
            AccountObj.activation_secret = auth.makesecret()
            AccountObj.is_verified = True
            user.save()
            AccountObj.save()

            return HttpResponse('Activated')

        return render(request, 'accounts/invalid_signup.html')
    else:
        return render(request, 'accounts/invalid_signup.html')
