from django.conf import settings

EMAIL_ACTIVATION = False    # Send Activation Email to user email
LOGIN_AFTER_ACTIVATION = True # Automatically Login User After Successfull Signup
RESET_PASSWORD_EXPIRY_TIME  = 5 # Reset Password Expiry Link  in minutes use Integer
SECRET = "".join(settings.SECRET_KEY) #Secret Key for JWT Encryption  & Decryption
EMAIL_FROM = 'Aartcy'
EMAIL_ACTIVATION_SUB = 'ACTIVATE YOUR ACCOUNT'  #email activation subject

HOST = settings.ALLOWED_HOSTS[0]
