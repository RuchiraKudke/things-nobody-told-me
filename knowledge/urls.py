from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views


urlpatterns = [

    # =====================================================
    # HOME
    # =====================================================

    path(
        "",
        views.home,
        name="home"
    ),

    # =====================================================
    # REGISTER
    # =====================================================

    path(
        "register/",
        views.register,
        name="register"
    ),

    # =====================================================
    # LOGIN
    # =====================================================

    path(
        "login/",
        views.user_login,
        name="login"
    ),

    # =====================================================
    # LOGOUT
    # =====================================================

    path(
        "logout/",
        views.user_logout,
        name="logout"
    ),

    # =====================================================
    # KNOWLEDGE DETAIL
    # =====================================================

    path(
        "knowledge/<int:pk>/",
        views.knowledge_detail,
        name="knowledge_detail"
    ),

    # =====================================================
    # SHARE TIP
    # =====================================================

    path(
        "share-tip/",
        views.share_tip,
        name="share_tip"
    ),

    # =====================================================
    # PASSWORD RESET - ENTER EMAIL
    # =====================================================

    path(
        "forgot-password/",
        auth_views.PasswordResetView.as_view(
            template_name="knowledge/forgot_password.html",

            email_template_name=(
                "knowledge/password_reset_email.txt"
            ),

            html_email_template_name=(
                "knowledge/password_reset_email.html"
            ),

            subject_template_name=(
                "knowledge/password_reset_subject.txt"
            ),

            success_url=reverse_lazy(
                "password_reset_done"
            ),
        ),
        name="password_reset"
    ),

    # =====================================================
    # PASSWORD RESET - EMAIL SENT
    # =====================================================

    path(
        "forgot-password/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name=(
                "knowledge/password_reset_done.html"
            )
        ),
        name="password_reset_done"
    ),

    # =====================================================
    # PASSWORD RESET - NEW PASSWORD
    # =====================================================

    path(
        "reset-password/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name=(
                "knowledge/password_reset_confirm.html"
            ),

            success_url=reverse_lazy(
                "password_reset_complete"
            ),
        ),
        name="password_reset_confirm"
    ),

    # =====================================================
    # PASSWORD RESET - COMPLETE
    # =====================================================

    path(
        "reset-password/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name=(
                "knowledge/password_reset_complete.html"
            )
        ),
        name="password_reset_complete"
    ),
]