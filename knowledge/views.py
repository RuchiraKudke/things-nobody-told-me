from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Knowledge, Location, Category, Vote


# =========================================================
# HOME
# =========================================================

def home(request):

    search_query = request.GET.get("search", "").strip()

    knowledge_list = (
        Knowledge.objects
        .filter(status="approved")
        .select_related("category", "location", "author")
        .order_by("-created_at")
    )

    if search_query:

        knowledge_list = knowledge_list.filter(
            title__icontains=search_query
        ) | knowledge_list.filter(
            description__icontains=search_query
        ) | knowledge_list.filter(
            category__name__icontains=search_query
        ) | knowledge_list.filter(
            location__name__icontains=search_query
        ) | knowledge_list.filter(
            location__city__icontains=search_query
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

    if request.method != "POST":
        return redirect("knowledge_detail", pk=pk)

    knowledge = get_object_or_404(
        Knowledge,
        pk=pk,
        status="approved",
    )

    vote_type = request.POST.get("vote_type")

    if vote_type not in ["agree", "disagree"]:
        return redirect(
            "knowledge_detail",
            pk=pk
        )

    vote, created = Vote.objects.get_or_create(
        user=request.user,
        knowledge=knowledge,
        defaults={
            "vote_type": vote_type
        }
    )

    # -------------------------------------------------
    # NEW VOTE
    # -------------------------------------------------

    if created:

        if vote_type == "agree":

            knowledge.confirmations += 1

        else:

            knowledge.disagreements += 1

    # -------------------------------------------------
    # EXISTING VOTE
    # -------------------------------------------------

    else:

        # Same vote clicked again → remove vote
        if vote.vote_type == vote_type:

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

        # Change vote
        else:

            if vote.vote_type == "agree":

                knowledge.confirmations = max(
                    0,
                    knowledge.confirmations - 1
                )

                knowledge.disagreements += 1

            else:

                knowledge.disagreements = max(
                    0,
                    knowledge.disagreements - 1
                )

                knowledge.confirmations += 1

            vote.vote_type = vote_type
            vote.save()

    knowledge.save()

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

        if not username or not email or not password or not confirm_password:

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
        # FIND USER
        # -------------------------------------------------

        user = User.objects.filter(
            username__iexact=login_input
        ).first()

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

        next_url = request.GET.get("next")

        if next_url:
            return redirect(next_url)

        return redirect("home")

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

        return redirect("home")

    return render(
        request,
        "knowledge/share_tip.html",
        {
            "categories": categories,
            "locations": locations,
        },
    )