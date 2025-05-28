from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.core.paginator import Paginator

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

from .models import UserProfile

def createacc(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to create an account.')
        return redirect('login')
    if not request.user.is_superuser:
        messages.error(request, 'Only the superuser can create accounts.')
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        address = request.POST.get('address')
        contact_number = request.POST.get('contact_number')
        position = request.POST.get('position')
        info_correct = request.POST.get('info_correct')

        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, 'createacc.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'createacc.html')

        try:
            user = User.objects.create_user(username=username, password=password)
            if full_name:
                name_parts = full_name.split()
                if len(name_parts) > 0:
                    user.first_name = name_parts[0]
                if len(name_parts) > 1:
                    user.last_name = ' '.join(name_parts[1:])
            user.save()
            # Create UserProfile with position
            UserProfile.objects.create(user=user, position=position)
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'createacc.html')

    return render(request, 'createacc.html')

@login_required
def profile(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        if password or password_confirm:
            if password != password_confirm:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'profile.html')
            if password:
                user.set_password(password)

        try:
            user.save()
            if password:
                update_session_auth_hash(request, user)  # Keep user logged in after password change
            messages.success(request, 'Profile updated successfully.')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')

    return render(request, 'profile.html')

@user_passes_test(lambda u: u.is_superuser)
def user_list(request):
    search_query = request.GET.get('search', '').strip()
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        is_superuser = request.POST.get('is_superuser') == 'on'
        password = request.POST.get('password', '').strip()

        try:
            user = User.objects.get(id=user_id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.is_active = is_active
            user.is_superuser = is_superuser
            if password:
                user.set_password(password)
            user.save()
            messages.success(request, f'User {user.username} updated successfully.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
        except Exception as e:
            messages.error(request, f'Error updating user: {str(e)}')

    if search_query:
        users = User.objects.filter(username__icontains=search_query)
    else:
        users = User.objects.all()
    paginator = Paginator(users, 5)  # Show 5 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'userlist.html', {'page_obj': page_obj, 'search_query': search_query})

from .models import Order
from django.views.decorators.csrf import csrf_exempt

from .models import UserProfile
from django.contrib.auth.decorators import login_required

@login_required
def form(request):
    # Allow superuser access immediately
    if request.user.is_superuser:
        pass
    else:
        # Check user position
        try:
            profile = request.user.profile
            if profile.position == 'Artist':
                messages.error(request, 'Artists are not allowed to create forms.')
                return redirect('order_list')
        except UserProfile.DoesNotExist:
            messages.error(request, 'User profile not found. Access denied.')
            return redirect('home')

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        received_date = request.POST.get('received_date')
        order_type = request.POST.get('order_type')
        due_date = request.POST.get('due_date')
        address = request.POST.get('address')
        contact_number = request.POST.get('contact_number')
        payment_type = request.POST.get('payment_type')
        price = request.POST.get('price')
        paid_amount = request.POST.get('paid_amount')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        if not customer_name or not received_date or not order_type or not due_date or not address or not contact_number or not payment_type or price is None or paid_amount is None:
            messages.error(request, 'Please fill out all required fields.')
            return render(request, 'form.html')

        try:
            order = Order(
                customer_name=customer_name,
                received_date=received_date,
                order_type=order_type,
                due_date=due_date,
                address=address,
                contact_number=contact_number,
                payment_type=payment_type,
                price=price,
                paid_amount=paid_amount,
                description=description,
                image=image
            )
            order.save()
            messages.success(request, 'Order created successfully.')
            return redirect('form')
        except Exception as e:
            messages.error(request, f'Error creating order: {str(e)}')
            return render(request, 'form.html')

    return render(request, 'form.html')

@login_required
def order_list(request):
    search_query = request.GET.get('search', '').strip()
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        paid_amount = request.POST.get('paid_amount')
        completed = request.POST.get('completed') == 'on'

        try:
            order = Order.objects.get(id=order_id)
            if paid_amount is not None:
                order.paid_amount = paid_amount
            order.completed = completed
            order.save()
            messages.success(request, f'Order {order.id} updated successfully.')
        except Order.DoesNotExist:
            messages.error(request, 'Order not found.')
        except Exception as e:
            messages.error(request, f'Error updating order: {str(e)}')

    if search_query:
        orders = Order.objects.filter(customer_name__icontains=search_query)
    else:
        orders = Order.objects.all()
    for order in orders:
        order.balance = float(order.price) - float(order.paid_amount)
    paginator = Paginator(orders, 5)  # Show 5 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'orderlist.html', {'page_obj': page_obj, 'search_query': search_query})


def order_update(request, order_id):
    from .models import Order
    from django.shortcuts import get_object_or_404
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.customer_name = request.POST.get('customer_name', order.customer_name)
        order.received_date = request.POST.get('received_date', order.received_date)
        order.order_type = request.POST.get('order_type', order.order_type)
        order.due_date = request.POST.get('due_date', order.due_date)
        order.address = request.POST.get('address', order.address)
        order.contact_number = request.POST.get('contact_number', order.contact_number)
        order.payment_type = request.POST.get('payment_type', order.payment_type)
        order.price = request.POST.get('price', order.price)
        order.paid_amount = request.POST.get('paid_amount', order.paid_amount)
        order.completed = request.POST.get('completed') == 'on'
        order.save()
        messages.success(request, f'Order {order.id} updated successfully.')
        return redirect('order_list')
    return render(request, 'order_update.html', {'order': order})

def order_delete(request, order_id):
    from .models import Order
    from django.shortcuts import get_object_or_404
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.delete()
        messages.success(request, f'Order {order.id} deleted successfully.')
        return redirect('order_list')
    return render(request, 'order_delete_confirm.html', {'order': order})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def forget_password(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        try:
            user = User.objects.get(username=username)
            if user.is_superuser:
                import random
                import string
                temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                user.set_password(temp_password)
                user.save()
                send_mail(
                    'Password Reset',
                    f'Your temporary password is: {temp_password}',
                    settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'admin@example.com',
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, 'Temporary password sent to your email.')
            else:
                messages.error(request, 'Password reset is only available for superusers.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
    return render(request, 'forget_password.html')
