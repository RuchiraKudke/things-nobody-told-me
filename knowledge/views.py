from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Knowledge, Location, Category


def home(request):

    search_query = request.GET.get('search', '')

    knowledge_list = Knowledge.objects.filter(
        status='approved'
    ).order_by('-created_at')

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

    return render(
        request,
        'knowledge/home.html',
        {
            'knowledge_list': knowledge_list,
            'search_query': search_query
        }
    )


def knowledge_detail(request, pk):

    knowledge = get_object_or_404(
        Knowledge,
        pk=pk,
        status='approved'
    )

    return render(
        request,
        'knowledge/detail.html',
        {
            'knowledge': knowledge
        }
    )


def register(request):

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not email or not password:
            messages.error(
                request,
                'Please fill in all required fields.'
            )
            return redirect('register')

        if password != confirm_password:
            messages.error(
                request,
                'Passwords do not match.'
            )
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(
                request,
                'Username already exists.'
            )
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        return redirect('home')

    return render(
        request,
        'knowledge/register.html'
    )


def user_login(request):

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('home')

        messages.error(
            request,
            'Invalid username or password.'
        )

        return redirect('login')

    return render(
        request,
        'knowledge/login.html'
    )


def user_logout(request):

    logout(request)

    return redirect('home')


@login_required
def share_tip(request):

    if request.method == 'POST':

        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category_id = request.POST.get('category')
        location_id = request.POST.get('location')

        # New location fields
        new_location_name = request.POST.get(
            'new_location_name',
            ''
        ).strip()

        new_location_city = request.POST.get(
            'new_location_city',
            ''
        ).strip()

        new_location_type = request.POST.get(
            'new_location_type',
            ''
        ).strip()

        # ---------------------------------
        # BASIC VALIDATION
        # ---------------------------------

        if not title or not description:
            messages.error(
                request,
                'Please enter a title and description.'
            )
            return redirect('share_tip')

        if not category_id:
            messages.error(
                request,
                'Please select a category.'
            )
            return redirect('share_tip')

        # ---------------------------------
        # CATEGORY VALIDATION
        # ---------------------------------

        category = get_object_or_404(
            Category,
            pk=category_id
        )

        # ---------------------------------
        # LOCATION HANDLING
        # ---------------------------------

        if location_id == 'new':

            # User selected "Other / Add New Location"

            if not new_location_name:
                messages.error(
                    request,
                    'Please enter the new location name.'
                )
                return redirect('share_tip')

            if not new_location_city:
                messages.error(
                    request,
                    'Please enter the city.'
                )
                return redirect('share_tip')

            if not new_location_type:
                new_location_type = 'Other'

            # Check whether same location already exists
            location = Location.objects.filter(
                name__iexact=new_location_name,
                city__iexact=new_location_city
            ).first()

            if location is None:

                location = Location.objects.create(
                    name=new_location_name,
                    city=new_location_city,
                    location_type=new_location_type
                )

        else:

            # Existing location selected

            if not location_id:
                messages.error(
                    request,
                    'Please select a location.'
                )
                return redirect('share_tip')

            location = get_object_or_404(
                Location,
                pk=location_id
            )

        # ---------------------------------
        # CREATE KNOWLEDGE
        # ---------------------------------

        Knowledge.objects.create(
            title=title,
            description=description,
            location=location,
            category=category,
            author=request.user,
            status='pending'
        )

        messages.success(
            request,
            'Your tip has been submitted for review.'
        )

        return redirect('home')

    # ---------------------------------
    # GET REQUEST
    # ---------------------------------

    locations = Location.objects.all().order_by(
        'city',
        'name'
    )

    categories = Category.objects.all().order_by(
        'name'
    )

    return render(
        request,
        'knowledge/share_tip.html',
        {
            'locations': locations,
            'categories': categories
        }
    )