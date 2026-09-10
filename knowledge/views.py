from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import Category, Knowledge, Location


# =========================================================
# HOME
# =========================================================

def home(request):

    search_query = request.GET.get("q", "").strip()

    knowledge_items = Knowledge.objects.filter(
        status="approved"
    ).select_related(
        "category",
        "location",
        "author"
    )

    if search_query:
        knowledge_items = knowledge_items.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(category__name__icontains=search_query)
            | Q(location__name__icontains=search_query)
            | Q(location__city__icontains=search_query)
        )

    knowledge_items = knowledge_items.order_by("-created_at")

    return render(
        request,
        "knowledge/home.html",
        {
            "knowledge_items": knowledge_items,
            "search_query": search_query,
        }
    )


# =========================================================
# KNOWLEDGE DETAIL
# =========================================================

def knowledge_detail(request, pk):

    knowledge = get_object_or_404(
        Knowledge.objects.select_related(
            "category",
            "location",
            "author"
        ),
        pk=pk,
        status="approved"
    )

    return render(
        request,
        "knowledge/detail.html",
        {
            "knowledge": knowledge
        }
    )


# =========================================================
# REGISTER
# =========================================================

def register(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()

        email = request.POST.get("email", "").strip().lower()

        password = request.POST.get("password", "")

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        # -------------------------
        # VALIDATION
        # -------------------------

        if not username:
            messages.error(
                request,
                "Username is required."
            )

            return render(
                request,
                "knowledge/register.html"
            )

        if not email:
            messages.error(
                request,
                "Email is required."
            )

            return render(
                request,
                "knowledge/register.html"
            )

        if not password:
            messages.error(
                request,
                "Password is required."
            )

            return render(
                request,
                "knowledge/register.html"
            )

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

        # -------------------------
        # CHECK USERNAME
        # -------------------------

        if User.objects.filter(
            username__iexact=username
        ).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return render(
                request,
                "knowledge/register.html"
            )

        # -------------------------
        # CHECK EMAIL
        # -------------------------

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

        # -------------------------
        # CREATE USER
        # -------------------------

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.is_active = True

        user.save()

        # -------------------------
        # LOGIN AFTER REGISTER
        # -------------------------

        login(
            request,
            user,
            backend="django.contrib.auth.backends.ModelBackend"
        )

        messages.success(
            request,
            "Account created successfully!"
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

        user = None

        # -------------------------------------------------
        # LOGIN USING USERNAME
        # -------------------------------------------------

        username_user = User.objects.filter(
            username__iexact=login_input
        ).first()

        if username_user:

            user = authenticate(
                request,
                username=username_user.username,
                password=password
            )

        # -------------------------------------------------
        # LOGIN USING EMAIL
        # -------------------------------------------------

        else:

            email_user = User.objects.filter(
                email__iexact=login_input
            ).first()

            if email_user:

                user = authenticate(
                    request,
                    username=email_user.username,
                    password=password
                )

        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        if user is not None and user.is_active:

            login(request, user)

            messages.success(
                request,
                f"Welcome back, {user.username}!"
            )

            next_url = request.GET.get("next")

            if next_url:
                return redirect(next_url)

            return redirect("home")

        # -------------------------------------------------
        # FAILURE
        # -------------------------------------------------

        messages.error(
            request,
            "Invalid username/email or password."
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

    return redirect("home")


# =========================================================
# SHARE TIP
# =========================================================

@login_required(login_url="login")
def share_tip(request):

    categories = Category.objects.all().order_by("name")

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
        )

        location_name = request.POST.get(
            "location_name",
            ""
        ).strip()

        city = request.POST.get(
            "city",
            ""
        ).strip()

        location_type = request.POST.get(
            "location_type",
            "General"
        ).strip()

        # -------------------------------------------------
        # VALIDATION
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
                    "categories": categories
                }
            )

        if not description:
            messages.error(
                request,
                "Description is required."
            )

            return render(
                request,
                "knowledge/share_tip.html",
                {
                    "categories": categories
                }
            )

        if not category_id:
            messages.error(
                request,
                "Please select a category."
            )

            return render(
                request,
                "knowledge/share_tip.html",
                {
                    "categories": categories
                }
            )

        # -------------------------------------------------
        # CATEGORY
        # -------------------------------------------------

        category = get_object_or_404(
            Category,
            id=category_id
        )

        # -------------------------------------------------
        # LOCATION
        # -------------------------------------------------

        if location_name and city:

            location, created = Location.objects.get_or_create(
                name=location_name,
                city=city,
                defaults={
                    "location_type": location_type
                }
            )

        else:

            messages.error(
                request,
                "Location name and city are required."
            )

            return render(
                request,
                "knowledge/share_tip.html",
                {
                    "categories": categories
                }
            )

        # -------------------------------------------------
        # CREATE KNOWLEDGE
        # -------------------------------------------------

        Knowledge.objects.create(
            title=title,
            description=description,
            location=location,
            category=category,
            author=request.user,
            status="pending"
        )

        messages.success(
            request,
            "Your tip has been submitted for approval."
        )

        return redirect("home")

    return render(
        request,
        "knowledge/share_tip.html",
        {
            "categories": categories
        }
    )