from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [

    # =========================================
    # HOME
    # =========================================

    path(
        '',
        views.home,
        name='home'
    ),


    # =========================================
    # KNOWLEDGE DETAIL
    # =========================================

    path(
        'knowledge/<int:pk>/',
        views.knowledge_detail,
        name='knowledge_detail'
    ),


    # =========================================
    # REGISTER
    # =========================================

    path(
        'register/',
        views.register,
        name='register'
    ),


    # =========================================
    # LOGIN
    # =========================================

    path(
        'login/',
        views.user_login,
        name='login'
    ),


    # =========================================
    # LOGOUT
    # =========================================

    path(
        'logout/',
        views.user_logout,
        name='logout'
    ),


    # =========================================
    # SHARE TIP
    # =========================================

    path(
        'share-tip/',
        views.share_tip,
        name='share_tip'
    ),


    # =========================================
    # PASSWORD RESET
    # =========================================

    # Step 1:
    # User enters registered email

    path(
        'forgot-password/',
        auth_views.PasswordResetView.as_view(
            template_name='knowledge/forgot_password.html'
        ),
        name='password_reset'
    ),


    # Step 2:
    # Password reset email sent page

    path(
        'forgot-password/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='knowledge/password_reset_done.html'
        ),
        name='password_reset_done'
    ),


    # Step 3:
    # User opens reset link from email

    path(
        'reset-password/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='knowledge/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),


    # Step 4:
    # Password successfully changed

    path(
        'reset-password/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='knowledge/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),

]