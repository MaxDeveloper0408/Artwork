from django.conf import settings

EMAIL_ACTIVATION = False  # Send Activation Email to user email
LOGIN_AFTER_ACTIVATION = True  # Automatically Login User After Successfull Signup
RESET_PASSWORD_EXPIRY_TIME = 5  # Reset Password Expiry Link  in minutes use Integer
SECRET = "".join(settings.SECRET_KEY)  # Secret Key for JWT Encryption  & Decryption
EMAIL_FROM = 'Webdevsmart@hotmail.com'
EMAIL_ACTIVATION_SUB = 'ACTIVATE YOUR ACCOUNT'  # email activation subject

SENDGRID_API_KEY = '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'

HOST = settings.ALLOWED_HOSTS[0]
