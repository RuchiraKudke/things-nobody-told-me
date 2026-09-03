from django.shortcuts import render, redirect
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

    knowledge = Knowledge.objects.get(
        pk=pk,
        status='approved'
    )

    return render(
        request,
        'knowledge/detail.html',
        {'knowledge': knowledge}
    )

def register(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        return redirect('home')

    return render(request, 'knowledge/register.html')


def user_login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('home')

        else:

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

        title = request.POST.get('title')
        description = request.POST.get('description')
        location_id = request.POST.get('location')
        category_id = request.POST.get('category')

        Knowledge.objects.create(
            title=title,
            description=description,
            location_id=location_id,
            category_id=category_id,
            author=request.user,
            status='pending'
        )

        return redirect('home')

    locations = Location.objects.all().order_by('city', 'name')
    categories = Category.objects.all().order_by('name')

    return render(
        request,
        'knowledge/share_tip.html',
        {
            'locations': locations,
            'categories': categories
        }
    )