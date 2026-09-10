from django.contrib import admin
from django.urls import include, path


urlpatterns = [

    # Admin
    path(
        "admin/",
        admin.site.urls
    ),

    # Knowledge application
    path(
        "",
        include("knowledge.urls")
    ),
]