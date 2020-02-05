from settings.models import StripeSetting,Menu,UserMenu,Quote

stripe_data =[ {
                    "name" : "PF",
                    "data" : "8",
                    "data_type" : "I"

                },
    {
                    "name" : "VI",
                    "data" : "208498080",
                    "data_type" : "S"

                },

                {
                    "name" : "SJ",
                    "data" : {
                              "type": "service_account",
                              "project_id": "aartcy",
                              "private_key_id": "ea8b25f329356ce0e38d504dd79e2c53d455e8dc",
                              "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDolNWkT4/8nU0t\nkGt0Dsv2WaNLd9gWumW7T6FTos/Y123Y1PYJ5KOsRFFIfyGfi7B0ibLseA+VwZx3\n1eKSVvBNVHfi7hCulFCbZW8MlZiNTjoGdNfElVEySzv1T0K+5KdgXH58uURaimLW\nan4FqlVEZmzy/USZ4Ev7boE9hZ78qLR4DURmXn5Y7Hsp4z9cyEyLdxjSpv1PDNf1\nAcKjiNHbw7kmew2YUY8FErVMB9yEnNWgHHVi1xfQc837xmIwNXy+kOAQefzAc3p7\nF85S6Mf93faoBxXrhXueNnWct0CwfIk74XF6oktRFF9vkvwUAtUuUqKdOY5gHHre\nJmqgBEWxAgMBAAECggEADRrVRJtHy/peRtPnTRBYH1juw7XkjOfK64RlrPtskg2V\n6ri5pgYuL3rAOHky1x05J6DaXjr32Fai2wj3+apIwxewQ17p/Vc9qTrceGldsZET\nwYk//ttxujdtYQGqu2wxbuNZTGxpOL+JSQbyM74krKxnhUO+Y7v01g2EflefBSH+\nGQx2540jOCy2yc1y9V52dkPetg1u8mCdeGpTcUbIwGjqOtmnKbISNOFmYFwO4kET\nY31rqExnbF5x1kYBJMFwAW7WMLSMf6UzuAyUEOXaOxVuYYEruvjh1dp6uaZfZSKD\n+o4su9OLcaIu/8luU/yq0KNuGIVlbA3qiYk9vzcsgQKBgQD8jrHCpY6qxsMiYa8j\npva90ZocLANkAaExQMCyE4oTQq4wGcvEIy5DxykUulQbS1YwetI+JVBNwhzF/ikx\nTQcKOhd8ztVqBk5rA3o9a226UUaku42FQp+Xr1KSgcrE5f/TCVlyi7s4iuprdrTW\n/0OTT/E/EGFMVsoEJJxe3SqkgQKBgQDrwG7vNryzG+VHmvb5imrMJ6hB38r2koEN\nnv+FtT8dxPgUUPCtj+YdsYzMiMfswZq6VmzSLYnKIwIhnzYeCMoj5KmGtr+inqSc\n2ocXjxvBcQLmP0x7gEK+lsj7rTrcxOZL2tB00oUu7yTnmFpqxuKrtEqFXysC6fwi\nH8WRoPJJMQKBgG2JVf+d3mqjGi7nPxava4SYS8a8MBxHuKmr8+dIIjKIURP7nCzN\nNVugHWkoByJvYkpUeqsJc/LFpcUZnrQLPGprF5TCAD2jzo8LSxEobsbISWNZFOAf\nLSiUmbOBJ3iOaI4XF/xeLi0v0swZCAXXYG+b1H4NlKWPXr69QjTCp6QBAoGBAK56\n5Z+160LESpUMY+2cPB6M20Kl1xlWpJzoKEVVNzlZJiIjJX3PGoivd32JXi4ju9hd\nTnzfpzMrZdBsfSkNaE3YVn+VkY9RypMsSP9usyQf9/1gq8Jb0wornuRl+UKbl7Zc\nZBuSE3ABHlcpswGD4Q8jiGPdY3/snObEjPyTGb6BAoGAagLhRDzXAE+nUfMeQesE\nmiT1fbhJpcX0GNx+TRwQCSRcFNdbVAUJi02ntlwQ9LMfjv5f/1QKGYk2G8cWATQp\nDUoagQF9MvNMfdLV/ScuVfmS+WIL+qmV3RfOvMG9dhlELyYyj+9n7b8JGNOmOegV\nUa9edSrsuO/91GzWC9ey/8M=\n-----END PRIVATE KEY-----\n",
                              "client_email": "aartcy-ga@aartcy.iam.gserviceaccount.com",
                              "client_id": "100187083286592396635",
                              "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                              "token_uri": "https://oauth2.googleapis.com/token",
                              "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                              "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/aartcy-ga%40aartcy.iam.gserviceaccount.com"
                            }
                    , "data_type" : "J"
                },


              ]
#stripe settings
def import_stripe_settings():

    for _ in stripe_data:

        try:
            obj = StripeSetting.objects.create(**_)
            print(obj.get_name_display() , 'added.')

        except:
            print('Setting already exists.')


#menu list

menu = ['Dashboard','Charges','Payouts','Buyers','Subscriptions','Shipping',
        'Tags','Colour codes','Achievements','Sold Out Art Shows','Fine Art Insurance',
        'Fine art Bank','Get LLC','Get copyright','Hire Tax Pro','Reports','FAQs','Support']

def menu_items():

    print('Deleting Old Data.')
    Menu.objects.all().delete()
    print('Deleted.')

    for m in menu:
        try:
            _ = Menu.objects.create(name=m)
            _.save()
        except:
            pass

    for m in Menu.objects.all():
        UserMenu.objects.create(menu=m).save()
        UserMenu.objects.create(menu=m,role='C').save()
        UserMenu.objects.create(menu=m,role='SA').save()


quotes = [
            "Like wildflower you must allow yourself to grow in all the places people thought you never would.",
            "MAYBE THE INTERNET RAISED US OR MAYBE PEOPLE ARE JERKS.",
          ]


def quote():
    for _ in quotes:
        Quote.objects.create(quote=_).save()
