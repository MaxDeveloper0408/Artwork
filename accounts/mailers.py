import smtplib
from .account_config import *
# from twilio.rest import Client
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import traceback

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def activation_text(token):
    return f'{settings.DOMAIN}/api/accounts/activate/{token}'


def activation_html(token):
    return f'<h5><a href="https://{settings.DOMAIN}/api/accounts/activate/{token}">Click here to activate account</a></h5>'


def reset_text(token):
    return f'{settings.DOMAIN}/reset-password/{token}'


def reset_html(token):
    return f'<h5><a href="https://{settings.DOMAIN}/reset-password/{token}">Click here to reset your password</a></h5>'


def send_email(to, subject, token, activation=True):
    if activation:
        text = activation_text(token)
        html = activation_html(token)
    else:
        text = reset_text(token)
        html = reset_html(token)
    #
    # from_email = EMAIL_FROM
    # msg = EmailMultiAlternatives(subject, text, from_email, [to])
    # msg.attach_alternative(html, "text/html")
    # msg.send()

    # return requests.post(
    #     "https://api.mailgun.net/v3/"+config.MAIL_GUN_DOMAIN+"/messages",   # domain url + /messages
    #     auth=("api", config.MAIL_GUN_API),                                  # api key in domain settings
    #     data={"from": "Diverse Aquaria <"+config.MAIL_GUN_FROM+">",            # mailgun @ domain.com (sandbox)
    #                   "to": to,                                             # add more email use list
    #           "subject": subject,
    #           "text": text,
    #           "html": html})

    message = Mail(
        from_email=EMAIL_FROM,
        to_emails=to,
        subject=subject,
        html_content=html)
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        print("Response status code: " + str(response.status_code))
        if response.status_code == 202:
            return True
        else:
            return False

        # print(response.body)
        # print(response.headers)
    except Exception as e:
        print("*************** Error ****************\n")
        traceback.print_exc()
        print("**************************************\n")
        return False


def send_buy_link(to, subject, link):
    text = f'{link}'
    html = f'<a href="{link}">Buy</a>'

    from_email = EMAIL_FROM
    msg = EmailMultiAlternatives(subject, text, from_email, [to])
    msg.attach_alternative(html, "text/html")
    msg.send()
