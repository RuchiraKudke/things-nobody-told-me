from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


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

    # =====================================================
    # FORGOT PASSWORD
    # =====================================================

    path(
        'forgot-password/',
        auth_views.PasswordResetView.as_view(
            template_name='knowledge/password_reset.html',
            email_template_name='knowledge/password_reset_email.html',
            success_url='/forgot-password/done/'
        ),
        name='password_reset'
    ),

    path(
        'forgot-password/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='knowledge/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path(
        'reset-password/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='knowledge/password_reset_confirm.html',
            success_url='/reset-password/complete/'
        ),
        name='password_reset_confirm'
    ),

    path(
        'reset-password/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='knowledge/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]