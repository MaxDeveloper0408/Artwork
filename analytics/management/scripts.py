from settings.models import StripeSetting,Menu,UserMenu,Quote

stripe_data =[ {
                    "name" : "PF",
                    "data" : "8",
                    "data_type" : "I"

                }
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
