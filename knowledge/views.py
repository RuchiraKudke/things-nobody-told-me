import os
import resend

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse

from .models import Knowledge, Location, Category, Vote


# =========================================================
# HOME
# =========================================================

def home(request):

    search_query = request.GET.get(
        "search",
        ""
    ).strip()

    knowledge_list = (
        Knowledge.objects
        .filter(status="approved")
        .select_related(
            "category",
            "location",
            "author"
        )
        .order_by("-created_at")
    )

    if search_query:

        knowledge_list = (
            knowledge_list.filter(
                title__icontains=search_query
            )
            | knowledge_list.filter(
                description__icontains=search_query
            )
            | knowledge_list.filter(
                category__name__icontains=search_query
            )
            | knowledge_list.filter(
                location__name__icontains=search_query
            )
            | knowledge_list.filter(
                location__city__icontains=search_query
            )
        )

        knowledge_list = knowledge_list.distinct()

    return render(
        request,
        "knowledge/home.html",
        {
            "knowledge_list": knowledge_list,
            "search_query": search_query,
        },
    )


# =========================================================
# KNOWLEDGE DETAIL
# =========================================================

def knowledge_detail(request, pk):

    knowledge = get_object_or_404(
        Knowledge.objects.select_related(
            "category",
            "location",
            "author",
        ),
        pk=pk,
        status="approved",
    )

    # -----------------------------------------------------
    # GET CURRENT USER'S VOTE
    # -----------------------------------------------------

    user_vote = None

    if request.user.is_authenticated:

        user_vote = Vote.objects.filter(
            user=request.user,
            knowledge=knowledge
        ).first()

    return render(
        request,
        "knowledge/detail.html",
        {
            "knowledge": knowledge,
            "user_vote": user_vote,
        },
    )


# =========================================================
# KNOWLEDGE VOTE
# =========================================================

@login_required(login_url="login")
def vote_knowledge(request, pk):

    # Only POST requests are allowed
    if request.method != "POST":

        return redirect(
            "knowledge_detail",
            pk=pk
        )

    # -----------------------------------------------------
    # GET KNOWLEDGE
    # -----------------------------------------------------

    knowledge = get_object_or_404(
        Knowledge,
        pk=pk,
        status="approved",
    )

    # -----------------------------------------------------
    # GET VOTE TYPE
    # -----------------------------------------------------

    vote_type = request.POST.get(
        "vote_type",
        ""
    ).strip()

    # Only these two values are accepted
    if vote_type not in [
        "agree",
        "disagree"
    ]:

        return redirect(
            "knowledge_detail",
            pk=pk
        )

    # -----------------------------------------------------
    # FIND EXISTING VOTE
    # -----------------------------------------------------

    vote = Vote.objects.filter(
        user=request.user,
        knowledge=knowledge
    ).first()

    # =====================================================
    # NO PREVIOUS VOTE
    # =====================================================

    if vote is None:

        Vote.objects.create(
            user=request.user,
            knowledge=knowledge,
            vote_type=vote_type,
        )

        if vote_type == "agree":

            knowledge.confirmations += 1

        else:

            knowledge.disagreements += 1

        knowledge.save(
            update_fields=[
                "confirmations",
                "disagreements",
            ]
        )

    # =====================================================
    # SAME VOTE AGAIN
    # =====================================================

    elif vote.vote_type == vote_type:

        # Remove existing vote

        if vote_type == "agree":

            knowledge.confirmations = max(
                0,
                knowledge.confirmations - 1
            )

        else:

            knowledge.disagreements = max(
                0,
                knowledge.disagreements - 1
            )

        vote.delete()

        knowledge.save(
            update_fields=[
                "confirmations",
                "disagreements",
            ]
        )

    # =====================================================
    # CHANGE VOTE
    # =====================================================

    else:

        # Previous vote was AGREE
        if vote.vote_type == "agree":

            knowledge.confirmations = max(
                0,
                knowledge.confirmations - 1
            )

            knowledge.disagreements += 1

        # Previous vote was DISAGREE
        else:

            knowledge.disagreements = max(
                0,
                knowledge.disagreements - 1
            )

            knowledge.confirmations += 1

        # Update user's vote
        vote.vote_type = vote_type

        vote.save(
            update_fields=[
                "vote_type"
            ]
        )

        knowledge.save(
            update_fields=[
                "confirmations",
                "disagreements",
            ]
        )

    # -----------------------------------------------------
    # RETURN TO DETAIL PAGE
    # -----------------------------------------------------

    return redirect(
        "knowledge_detail",
        pk=pk
    )


# =========================================================
# REGISTER
# =========================================================

def register(request):

    if request.user.is_authenticated:

        return redirect("home")

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip().lower()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------

        if (
            not username
            or not email
            or not password
            or not confirm_password
        ):

            messages.error(
                request,
                "Please fill in all fields."
            )

            return render(
                request,
                "knowledge/register.html"
            )

        # -------------------------------------------------
        # USERNAME
        # -------------------------------------------------

        if User.objects.filter(
            username__iexact=username
        ).exists():

            messages.error(
                request,
                "Username already exists. Please choose another username."
            )

            return render(
                request,
                "knowledge/register.html"
            )

        # -------------------------------------------------
        # EMAIL
        # -------------------------------------------------

        if User.objects.filter(
            email__iexact=email
        ).exists():

            messages.error(
                request,
                "An account with this email already exists."
            )

            return render(
                request,
                "knowledge/register.html"
            )

        # -------------------------------------------------
        # PASSWORD
        # -------------------------------------------------

        if len(password) < 8:

            messages.error(
                request,
                "Password must contain at least 8 characters."
            )

            return render(
                request,
                "knowledge/register.html"
            )

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return render(
                request,
                "knowledge/register.html"
            )

        # -------------------------------------------------
        # CREATE USER
        # -------------------------------------------------

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        user.is_active = True
        user.save()

        # -------------------------------------------------
        # AUTOMATIC LOGIN
        # -------------------------------------------------

        login(
            request,
            user,
            backend="django.contrib.auth.backends.ModelBackend",
        )

        messages.success(
            request,
            f"Account created successfully! Welcome, {user.username}."
        )

        return redirect("home")

    return render(
        request,
        "knowledge/register.html"
    )


# =========================================================
# LOGIN
# =========================================================

def user_login(request):

    if request.user.is_authenticated:

        return redirect("home")

    if request.method == "POST":

        login_input = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not login_input or not password:

            messages.error(
                request,
                "Please enter your username/email and password."
            )

            return render(
                request,
                "knowledge/login.html"
            )

        # -------------------------------------------------
        # FIND USER BY USERNAME
        # -------------------------------------------------

        user = User.objects.filter(
            username__iexact=login_input
        ).first()

        # -------------------------------------------------
        # FIND USER BY EMAIL
        # -------------------------------------------------

        if user is None:

            user = User.objects.filter(
                email__iexact=login_input
            ).first()

        # -------------------------------------------------
        # USER NOT FOUND
        # -------------------------------------------------

        if user is None:

            messages.error(
                request,
                "Invalid username/email or password."
            )

            return render(
                request,
                "knowledge/login.html"
            )

        # -------------------------------------------------
        # CHECK ACTIVE
        # -------------------------------------------------

        if not user.is_active:

            messages.error(
                request,
                "This account is inactive."
            )

            return render(
                request,
                "knowledge/login.html"
            )

        # -------------------------------------------------
        # CHECK PASSWORD
        # -------------------------------------------------

        authenticated_user = authenticate(
            request,
            username=user.username,
            password=password,
        )

        if authenticated_user is None:

            messages.error(
                request,
                "Invalid username/email or password."
            )

            return render(
                request,
                "knowledge/login.html"
            )

        # -------------------------------------------------
        # LOGIN
        # -------------------------------------------------

        login(
            request,
            authenticated_user,
            backend="django.contrib.auth.backends.ModelBackend",
        )

        messages.success(
            request,
            f"Welcome back, {authenticated_user.username}!"
        )

        # -------------------------------------------------
        # NEXT URL
        # -------------------------------------------------

        next_url = request.GET.get(
            "next"
        )

        if next_url:

            return redirect(
                next_url
            )

        return redirect(
            "home"
        )

    return render(
        request,
        "knowledge/login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@login_required(login_url="login")
def user_logout(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect(
        "home"
    )


# =========================================================
# SHARE TIP
# =========================================================

@login_required(login_url="login")
def share_tip(request):

    categories = Category.objects.all().order_by(
        "name"
    )

    locations = Location.objects.all().order_by(
        "city",
        "name"
    )

    if request.method == "POST":

        title = request.POST.get(
            "title",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        category_id = request.POST.get(
            "category",
            ""
        ).strip()

        location_id = request.POST.get(
            "location",
            ""
        ).strip()

        new_location_name = request.POST.get(
            "new_location_name",
            ""
        ).strip()

        new_location_city = request.POST.get(
            "new_location_city",
            ""
        ).strip()

        new_location_type = request.POST.get(
            "new_location_type",
            ""
        ).strip()

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        if not title:

            messages.error(
                request,
                "Title is required."
            )

            return render(
                request,
                "knowledge/share_tip.html",
                {
                    "categories": categories,
                    "locations": locations,
                },
            )

        # -------------------------------------------------
        # DESCRIPTION
        # -------------------------------------------------

        if not description:

            messages.error(
                request,
                "Description is required."
            )

            return render(
                request,
                "knowledge/share_tip.html",
                {
                    "categories": categories,
                    "locations": locations,
                },
            )

        # -------------------------------------------------
        # CATEGORY
        # -------------------------------------------------

        if not category_id:

            messages.error(
                request,
                "Please select a category."
            )

            return render(
                request,
                "knowledge/share_tip.html",
                {
                    "categories": categories,
                    "locations": locations,
                },
            )

        category = get_object_or_404(
            Category,
            pk=category_id
        )

        # -------------------------------------------------
        # LOCATION
        # -------------------------------------------------

        if location_id == "new":

            if not new_location_name:

                messages.error(
                    request,
                    "Please enter the new location name."
                )

                return render(
                    request,
                    "knowledge/share_tip.html",
                    {
                        "categories": categories,
                        "locations": locations,
                    },
                )

            if not new_location_city:

                messages.error(
                    request,
                    "Please enter the city."
                )

                return render(
                    request,
                    "knowledge/share_tip.html",
                    {
                        "categories": categories,
                        "locations": locations,
                    },
                )

            if not new_location_type:

                new_location_type = "Other"

            location = Location.objects.filter(
                name__iexact=new_location_name,
                city__iexact=new_location_city,
            ).first()

            if location is None:

                location = Location.objects.create(
                    name=new_location_name,
                    city=new_location_city,
                    location_type=new_location_type,
                )

        else:

            if not location_id:

                messages.error(
                    request,
                    "Please select a location."
                )

                return render(
                    request,
                    "knowledge/share_tip.html",
                    {
                        "categories": categories,
                        "locations": locations,
                    },
                )

            location = get_object_or_404(
                Location,
                pk=location_id
            )

        # -------------------------------------------------
        # CREATE TIP
        # -------------------------------------------------

        Knowledge.objects.create(
            title=title,
            description=description,
            location=location,
            category=category,
            author=request.user,
            status="pending",
        )

        messages.success(
            request,
            "Your tip has been submitted for review."
        )

        return redirect(
            "home"
        )

    return render(
        request,
        "knowledge/share_tip.html",
        {
            "categories": categories,
            "locations": locations,
        },
    )


# =========================================================
# FORGOT PASSWORD
# =========================================================

def forgot_password(request):

    if request.method == "POST":

        email = request.POST.get(
            "email",
            ""
        ).strip().lower()

        # -------------------------------------------------
        # EMAIL REQUIRED
        # -------------------------------------------------

        if not email:

            messages.error(
                request,
                "Please enter your email address."
            )

            return render(
                request,
                "knowledge/forgot_password.html"
            )

        # -------------------------------------------------
        # FIND USER
        # -------------------------------------------------

        user = User.objects.filter(
            email__iexact=email,
            is_active=True
        ).first()

        if user is None:

            messages.error(
                request,
                "No account was found with this email address."
            )

            return render(
                request,
                "knowledge/forgot_password.html"
            )

        # -------------------------------------------------
        # CREATE RESET TOKEN
        # -------------------------------------------------

        uid = urlsafe_base64_encode(
            force_bytes(user.pk)
        )

        token = default_token_generator.make_token(
            user
        )

        # -------------------------------------------------
        # CREATE RESET URL
        # -------------------------------------------------

        reset_url = request.build_absolute_uri(
            reverse(
                "password_reset_confirm",
                kwargs={
                    "uidb64": uid,
                    "token": token,
                }
            )
        )

        # -------------------------------------------------
        # RESEND API KEY
        # -------------------------------------------------

        resend.api_key = os.environ.get(
            "RESEND_API_KEY"
        )

        # -------------------------------------------------
        # SEND EMAIL
        # -------------------------------------------------

        try:

            resend.Emails.send(
                {
                    "from": (
                        "Things Nobody Told Me "
                        "<onboarding@resend.dev>"
                    ),

                    "to": [
                        user.email
                    ],

                    "subject": (
                        "Reset your password | "
                        "Things Nobody Told Me"
                    ),

                    "html": f"""
                        <div style="
                            font-family: Arial, sans-serif;
                            max-width: 600px;
                            margin: auto;
                            padding: 30px;
                            color: #222;
                        ">

                            <h2>
                                Reset your password
                            </h2>

                            <p>
                                Hi {user.username},
                            </p>

                            <p>
                                We received a request to reset
                                the password for your
                                Things Nobody Told Me account.
                            </p>

                            <p>
                                Click the button below to
                                create a new password:
                            </p>

                            <p>
                                <a
                                    href="{reset_url}"
                                    style="
                                        display: inline-block;
                                        padding: 12px 20px;
                                        background: #222;
                                        color: white;
                                        text-decoration: none;
                                        border-radius: 8px;
                                    "
                                >
                                    Reset Password
                                </a>
                            </p>

                            <p>
                                This link will expire
                                automatically.
                            </p>

                            <p>
                                If you did not request a
                                password reset, you can safely
                                ignore this email.
                            </p>

                            <p>
                                — Things Nobody Told Me
                            </p>

                        </div>
                    """
                }
            )

        except Exception:

            messages.error(
                request,
                "Unable to send the reset email right now. Please try again later."
            )

            return render(
                request,
                "knowledge/forgot_password.html"
            )

        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        messages.success(
            request,
            "Password reset link has been sent to your email."
        )

        return redirect(
            "password_reset_done"
        )

    # -----------------------------------------------------
    # GET REQUEST
    # -----------------------------------------------------

    return render(
        request,
        "knowledge/forgot_password.html"
    )