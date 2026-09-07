```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Knowledge, Location, Category


# =========================================================
# HOME
# =========================================================

def home(request):

    search_query = request.GET.get('search', '').strip()

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

        knowledge_list = knowledge_list.distinct()

    return render(
        request,
        'knowledge/home.html',
        {
            'knowledge_list': knowledge_list,
            'search_query': search_query
        }
    )


# =========================================================
# KNOWLEDGE DETAIL
# =========================================================

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


# =========================================================
# REGISTER
# =========================================================

def register(request):

    if request.method == 'POST':

        username = request.POST.get(
            'username',
            ''
        ).strip()

        email = request.POST.get(
            'email',
            ''
        ).strip().lower()

        password = request.POST.get(
            'password',
            ''
        )

        confirm_password = request.POST.get(
            'confirm_password',
            ''
        )

        # -----------------------------------------
        # BASIC VALIDATION
        # -----------------------------------------

        if not username or not email or not password or not confirm_password:

            messages.error(
                request,
                'Please fill in all fields.'
            )

            return redirect('register')

        # -----------------------------------------
        # USERNAME VALIDATION
        # -----------------------------------------

        if User.objects.filter(
            username__iexact=username
        ).exists():

            messages.error(
                request,
                'Username already exists. Please choose another username.'
            )

            return redirect('register')

        # -----------------------------------------
        # EMAIL VALIDATION
        # -----------------------------------------

        if User.objects.filter(
            email__iexact=email
        ).exists():

            messages.error(
                request,
                'An account with this email already exists.'
            )

            return redirect('register')

        # -----------------------------------------
        # PASSWORD VALIDATION
        # -----------------------------------------

        if len(password) < 8:

            messages.error(
                request,
                'Password must contain at least 8 characters.'
            )

            return redirect('register')

        if password != confirm_password:

            messages.error(
                request,
                'Passwords do not match.'
            )

            return redirect('register')

        # -----------------------------------------
        # CREATE USER
        # -----------------------------------------

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Make sure the account is active
        user.is_active = True
        user.save()

        # -----------------------------------------
        # AUTOMATIC LOGIN
        # -----------------------------------------

        login(
            request,
            user
        )

        messages.success(
            request,
            f'Registration successful! Welcome, {user.username}.'
        )

        return redirect('home')

    # -----------------------------------------
    # GET REQUEST
    # -----------------------------------------

    return render(
        request,
        'knowledge/register.html'
    )


# =========================================================
# LOGIN
# =========================================================

def user_login(request):

    if request.method == 'POST':

        login_input = request.POST.get(
            'username',
            ''
        ).strip()

        password = request.POST.get(
            'password',
            ''
        )

        # -----------------------------------------
        # BASIC VALIDATION
        # -----------------------------------------

        if not login_input or not password:

            messages.error(
                request,
                'Please enter your username/email and password.'
            )

            return redirect('login')

        user = None

        # -----------------------------------------
        # LOGIN USING USERNAME
        # -----------------------------------------

        user = authenticate(
            request,
            username=login_input,
            password=password
        )

        # -----------------------------------------
        # LOGIN USING EMAIL
        # -----------------------------------------

        if user is None:

            matching_user = User.objects.filter(
                email__iexact=login_input
            ).first()

            if matching_user:

                user = authenticate(
                    request,
                    username=matching_user.username,
                    password=password
                )

        # -----------------------------------------
        # CHECK LOGIN RESULT
        # -----------------------------------------

        if user is not None:

            if not user.is_active:

                messages.error(
                    request,
                    'This account is inactive. Please contact the administrator.'
                )

                return redirect('login')

            login(
                request,
                user
            )

            messages.success(
                request,
                f'Welcome back, {user.username}!'
            )

            return redirect('home')

        # -----------------------------------------
        # LOGIN FAILED
        # -----------------------------------------

        messages.error(
            request,
            'Invalid username/email or password.'
        )

        return redirect('login')

    # -----------------------------------------
    # GET REQUEST
    # -----------------------------------------

    return render(
        request,
        'knowledge/login.html'
    )


# =========================================================
# FORGOT PASSWORD / RESET PASSWORD
# =========================================================

def forgot_password(request):

    if request.method == 'POST':

        action = request.POST.get(
            'action',
            'check_email'
        )

        # -----------------------------------------
        # CHECK EMAIL
        # -----------------------------------------

        if action == 'check_email':

            email = request.POST.get(
                'email',
                ''
            ).strip().lower()

            if not email:

                messages.error(
                    request,
                    'Please enter your email address.'
                )

                return redirect('forgot_password')

            user = User.objects.filter(
                email__iexact=email
            ).first()

            if user is None:

                messages.error(
                    request,
                    'No account found with this email address.'
                )

                return redirect('forgot_password')

            return render(
                request,
                'knowledge/forgot_password.html',
                {
                    'reset_user': user,
                    'email_verified': True
                }
            )

        # -----------------------------------------
        # RESET PASSWORD
        # -----------------------------------------

        elif action == 'reset_password':

            user_id = request.POST.get(
                'user_id'
            )

            new_password = request.POST.get(
                'new_password',
                ''
            )

            confirm_password = request.POST.get(
                'confirm_password',
                ''
            )

            user = get_object_or_404(
                User,
                pk=user_id
            )

            # -------------------------------------
            # PASSWORD VALIDATION
            # -------------------------------------

            if not new_password:

                messages.error(
                    request,
                    'Please enter a new password.'
                )

                return render(
                    request,
                    'knowledge/forgot_password.html',
                    {
                        'reset_user': user,
                        'email_verified': True
                    }
                )

            if len(new_password) < 8:

                messages.error(
                    request,
                    'Password must contain at least 8 characters.'
                )

                return render(
                    request,
                    'knowledge/forgot_password.html',
                    {
                        'reset_user': user,
                        'email_verified': True
                    }
                )

            if new_password != confirm_password:

                messages.error(
                    request,
                    'Passwords do not match.'
                )

                return render(
                    request,
                    'knowledge/forgot_password.html',
                    {
                        'reset_user': user,
                        'email_verified': True
                    }
                )

            # -------------------------------------
            # UPDATE PASSWORD
            # -------------------------------------

            user.set_password(
                new_password
            )

            user.save()

            messages.success(
                request,
                'Password reset successfully. Please login with your new password.'
            )

            return redirect('login')

    # -----------------------------------------
    # GET REQUEST
    # -----------------------------------------

    return render(
        request,
        'knowledge/forgot_password.html'
    )


# =========================================================
# LOGOUT
# =========================================================

def user_logout(request):

    logout(request)

    messages.success(
        request,
        'You have been logged out successfully.'
    )

    return redirect('home')


# =========================================================
# SHARE TIP
# =========================================================

@login_required
def share_tip(request):

    if request.method == 'POST':

        # -----------------------------------------
        # GET FORM DATA
        # -----------------------------------------

        title = request.POST.get(
            'title',
            ''
        ).strip()

        description = request.POST.get(
            'description',
            ''
        ).strip()

        category_id = request.POST.get(
            'category',
            ''
        ).strip()

        location_id = request.POST.get(
            'location',
            ''
        ).strip()

        # -----------------------------------------
        # NEW LOCATION DATA
        # -----------------------------------------

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

        # -----------------------------------------
        # BASIC VALIDATION
        # -----------------------------------------

        if not title:

            messages.error(
                request,
                'Please enter a title.'
            )

            return redirect('share_tip')

        if not description:

            messages.error(
                request,
                'Please enter a description.'
            )

            return redirect('share_tip')

        if not category_id:

            messages.error(
                request,
                'Please select a category.'
            )

            return redirect('share_tip')

        # -----------------------------------------
        # CATEGORY
        # -----------------------------------------

        category = get_object_or_404(
            Category,
            pk=category_id
        )

        # -----------------------------------------
        # LOCATION
        # -----------------------------------------

        if location_id == 'new':

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

            # -------------------------------------
            # CHECK EXISTING LOCATION
            # -------------------------------------

            location = Location.objects.filter(
                name__iexact=new_location_name,
                city__iexact=new_location_city
            ).first()

            # -------------------------------------
            # CREATE NEW LOCATION
            # -------------------------------------

            if location is None:

                location = Location.objects.create(
                    name=new_location_name,
                    city=new_location_city,
                    location_type=new_location_type
                )

        else:

            # -------------------------------------
            # EXISTING LOCATION
            # -------------------------------------

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

        # -----------------------------------------
        # CREATE KNOWLEDGE
        # -----------------------------------------

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

    # -----------------------------------------
    # GET REQUEST
    # -----------------------------------------

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
```
