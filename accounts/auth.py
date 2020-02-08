import jwt
import random
import string
import binascii
import os

from datetime import datetime, date, timedelta
from .account_config import SECRET, RESET_PASSWORD_EXPIRY_TIME


# account custom fuctions

def valid_date(token_date):
    # check token valid date
    current_date = datetime.now().date()
    striped_date = datetime.strptime(token_date, '%y, %m %d').date()
    Date = current_date - striped_date
    if not Date:
        return True
    else:
        return False


def valid_time(token_time):
    # check valid time
    current_time = datetime.now().time()
    stoken_time = datetime.strptime(token_time, '%H,%M,%S').time()
    str_ctime = str(current_time)
    str_Ttime = str(stoken_time)
    stripd_Ctime = str_ctime[:str_ctime.rfind(':')]
    stripd_Ttime = str_Ttime[:str_Ttime.rfind(':')]

    ctH, ctM = stripd_Ctime[:stripd_Ctime.rfind(':')], stripd_Ctime[stripd_Ctime.rfind(':') + 1:]
    TtH, TtM = stripd_Ttime[:stripd_Ttime.rfind(':')], stripd_Ttime[stripd_Ttime.rfind(':') + 1:]
    current = timedelta(hours=int(ctH), minutes=int(ctM))
    TOKEN_TIME = timedelta(hours=int(TtH), minutes=int(TtM))
    getTime = current - TOKEN_TIME
    hours_minutes = str(getTime)[:str(getTime).rfind(':')]
    Hours = int(hours_minutes[:hours_minutes.rfind(':')])
    Minutes = int(hours_minutes[hours_minutes.rfind(':') + 1:])
    if Hours == 0 and Minutes <= RESET_PASSWORD_EXPIRY_TIME:
        return True
    else:
        return False


def makesecret(username_or_any=False):
    if username_or_any:
        return f'{username_or_any}_{binascii.hexlify(os.urandom(20)).decode()}'
    return binascii.hexlify(os.urandom(20)).decode()


def secretMessage(messge):
    # create secret message
    data = {'message': messge}
    return jwt.encode(data, SECRET, algorithm='HS256').decode('ascii')


# make JWT(JWT: JSON Web Token)
def make_jwt(username, activation_secret):
    # make simple jwt with username & profile token
    data = {'key': activation_secret, 'username': username}
    return jwt.encode(data, SECRET, algorithm='HS256').decode('ascii')


def make_expiry_JWT(username, secret):
    # make jwt with expiry
    d = datetime.now()
    data = {'key': secret, 'username': username,
            'time': d.time().strftime("%H,%M,%S"),
            'date': d.date().strftime('%y, %m %d')}

    return jwt.encode(data, SECRET, algorithm='HS256').decode('ascii')


def checkJWT(secret):
    # check for jwt
    try:
        token = jwt.decode(secret, SECRET, algorithms=['HS256'])
    except:
        token = {}
    return token


def checkExpiryJWT(secret):
    # check for jwt with expiry
    try:
        token = jwt.decode(secret, SECRET, algorithms=['HS256'])
        token_date = valid_date(token['date'])
        token_time = valid_time(token['time'])
        if token_date and token_time:
            return token
        else:
            token = {}
    except:
        token = {}
    return token
