import smtplib
from .account_config import *
# from twilio.rest import Client
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def TEXT(token):
    return f'{HOST}/api/accounts/activate/{token}'

def HTML(token):
    return f'<h5><a href="{HOST}/api/accounts/activate/{token}">Click here to activate account</a></h5>'

def ResetTEXT(token):
    return f'{HOST}/reset-password/{token}'

def ResetHTML(token):
    return f'<h5><a href="{HOST}/reset-password/{token}">Click here to reset yourpassword</a></h5>'

def SendEmail(to,subject,token,activation=True):

    if activation:
        text = TEXT(token)
        html = HTML(token)
    else:
        text = ResetTEXT(token)
        html = ResetHTML(token)


    from_email = EMAIL_FROM
    msg = EmailMultiAlternatives(subject, text, from_email, [to])
    msg.attach_alternative(html, "text/html")
    msg.send()

    # return requests.post(
    #     "https://api.mailgun.net/v3/"+config.MAIL_GUN_DOMAIN+"/messages",   # domain url + /messages
    #     auth=("api", config.MAIL_GUN_API),                                  # api key in domain settings
    #     data={"from": "Diverse Aquaria <"+config.MAIL_GUN_FROM+">",            # mailgun @ domain.com (sandbox)
    #                   "to": to,                                             # add more email use list
    #           "subject": subject,
    #           "text": text,
    #           "html": html})


def send_buy_link(to,subject,link):

    text = f'{link}'
    html = f'<a href="{link}">Buy</a>'

    from_email = EMAIL_FROM
    msg = EmailMultiAlternatives(subject, text, from_email, [to])
    msg.attach_alternative(html, "text/html")
    msg.send()
