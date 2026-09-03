from django.urls import path
from . import views


urlpatterns = [

    path(
        '',
        views.home,
        name='home'
    ),

    path(
        'knowledge/<int:pk>/',
        views.knowledge_detail,
        name='knowledge_detail'
    ),

    path(
        'register/',
        views.register,
        name='register'
    ),

    path(
        'login/',
        views.user_login,
        name='login'
    ),

    path(
        'logout/',
        views.user_logout,
        name='logout'
    ),

    path(
        'share-tip/',
        views.share_tip,
        name='share_tip'
    ),
]