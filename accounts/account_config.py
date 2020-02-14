from django.conf import settings

EMAIL_ACTIVATION = False  # Send Activation Email to user email
LOGIN_AFTER_ACTIVATION = True  # Automatically Login User After Successfull Signup
RESET_PASSWORD_EXPIRY_TIME = 5  # Reset Password Expiry Link  in minutes use Integer
SECRET = "".join(settings.SECRET_KEY)  # Secret Key for JWT Encryption  & Decryption
EMAIL_ACTIVATION_SUB = 'ACTIVATE YOUR ACCOUNT'  # email activation subject

SENDGRID_API_KEY = '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'

if settings.DEBUG is True:
    # development mode, use my email
    EMAIL_FROM = 'Webdevsmart@hotmail.com'
else:
    # production mode, use real email
    EMAIL_FROM = settings.EMAIL_HOST_USER
