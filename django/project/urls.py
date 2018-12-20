from django.contrib import admin
from django.urls import path

import cluster.views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', cluster.views.IndexView.as_view(), name='home'),
]
