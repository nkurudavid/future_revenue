from django.contrib import admin
from django.urls import path, include

from django.conf import settings

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('future_revenue.urls')),
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# THE FOLLOWING FUNCTION WILL HELP US TO HANDLE THE UNAVAILABLE LINK OR WEB PAGE
handler404 = "future_revenue.views.handle_not_found"


# Configure Admin Title
admin.site.site_header = "ESTIMATING FUTURE REVENUE BY PREDICTING THE AMOUNT OF PRODUCT"
admin.site.index_title = "MANAGEMENT"
admin.site.site_title = "Control Panel"
