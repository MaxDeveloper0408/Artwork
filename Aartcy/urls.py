from django.contrib import admin
from django.conf import settings
from django.urls import path,include,re_path
from payments.views import CheckoutViaLink
from django.conf.urls.static import static
from django.views.generic.base import TemplateView

urlpatterns = [
    path('dj-admin/', admin.site.urls),
    path('api/v1/accounts/',include('accounts.urls')),
    path('api/v1/arts/',include('arts.urls')),
    path('api/v1/payments/',include('payments.urls')),
    path('api/v1/settings/',include('settings.urls')),
    path('api/v1/analytics/',include('analytics.urls')),

]


#Media & Static Urls

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
            +  static(settings.STATIC_URL, document_root=settings.STATIC_URL)

urlpatterns.append(re_path('^.*', TemplateView.as_view(template_name = "base.html"), name="base"))
