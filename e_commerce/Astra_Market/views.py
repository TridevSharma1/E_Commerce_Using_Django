import base64
import hashlib
import hmac
import json
import urllib.request

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.text import slugify
from decimal import Decimal
from datetime import datetime
from .models import CustomUser, Feedback, Product, Category, CartItem, WishlistItem, Order, OrderItem
from django.views.decorators.http import require_POST


def home(request):
    """
    Home page view.
    """
    featured_products = Product.objects.all()[:4]
    return render(request, 'home.html', {'featured_products': featured_products})


def register(request):
    """
    User registration view.
    Handles both GET (display form) and POST (process registration).
    """
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Validation
        if not all([full_name, email, mobile, password, confirm_password]):
            messages.error(request, 'All fields are required.')
            return redirect('register')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')
        
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return redirect('register')

        if request.POST.get('accept_terms') != 'on':
            messages.error(request, 'You must agree to the Terms & Conditions to create an account.')
            return redirect('register')
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('register')

        if CustomUser.objects.filter(mobile=mobile).exists():
            messages.error(request, 'This mobile number is already registered.')
            return redirect('register')
        
        try:
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                full_name=full_name,
                mobile=mobile,
            )
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return redirect('register')
    
    return render(request, 'register.html')


def user_login(request):
    """
    User login view.
    Authenticates user with email and password.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Email and password are required.')
            return redirect('login')
        
        try:
            user = CustomUser.objects.get(email=email)
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.full_name}!')
                return redirect('home')  # Change 'home' to your home page URL name
            else:
                messages.error(request, 'Invalid email or password.')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'login.html')


@login_required(login_url='login')
def user_logout(request):
    """
    User logout view.
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required(login_url='login')
def profile(request):
    """
    User profile view.
    Displays and updates the logged-in user's profile information.
    """
    user = request.user

    if request.method == 'POST' and 'delete_account' not in request.POST:
        full_name = request.POST.get('full_name', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        alternate_mobile = request.POST.get('alternate_mobile', '').strip()
        dob = request.POST.get('dob', '').strip()
        gender = request.POST.get('gender', '').strip()
        address = request.POST.get('address', '').strip()
        profile_image = request.FILES.get('profile_image')

        if not full_name or not mobile:
            messages.error(request, 'Full name and primary mobile number are required.')
            return redirect('profile')

        user.full_name = full_name
        user.mobile = mobile
        user.alternate_mobile = alternate_mobile or None
        user.dob = dob or None
        user.gender = gender or ''
        user.address = address or ''

        if profile_image:
            user.profile_image = profile_image

        try:
            user.full_clean()
            user.save()
            messages.success(request, 'Your profile has been updated successfully.')
        except ValidationError as e:
            messages.error(request, 'Please correct the profile information.')
            for field_errors in e.message_dict.values():
                for error in field_errors:
                    messages.error(request, error)

        return redirect('profile')

    return render(request, 'profile.html', {'user': user})


@login_required(login_url='login')
def delete_account(request):
    """
    Delete the logged-in user's account.
    """
    if request.method == 'POST':
        user = request.user
        user.delete()
        logout(request)
        messages.success(request, 'Your account has been deleted successfully.')
    return redirect('register')


def about(request):
    """
    About page.
    """
    return render(request, 'about.html')


def terms(request):
    """
    Terms & conditions page.
    """
    return render(request, 'terms.html')


def products(request):
    """
    Products listing page and staff-only creation form.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated or not request.user.is_staff:
            messages.error(request, 'Only staff users can add products.')
            return redirect('products')

        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price', '').strip()
        category_id = request.POST.get('category')
        image = request.FILES.get('image')

        if not all([title, price, category_id]):
            messages.error(request, 'Title, price, and category are required.')
            return redirect('products')

        category = get_object_or_404(Category, id=category_id)
        slug = slugify(title)
        counter = 1
        while Product.objects.filter(slug=slug).exists():
            slug = f'{slugify(title)}-{counter}'
            counter += 1

        Product.objects.create(
            title=title,
            slug=slug,
            category=category,
            description=description,
            price=Decimal(price),
            image=image,
        )
        messages.success(request, f'Product "{title}" created successfully.')
        return redirect('products')

    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    products = Product.objects.all()
    categories = Category.objects.all()
    selected_category_name = ''

    if query:
        products = products.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if category_slug:
        category = Category.objects.filter(slug=category_slug).first()
        if category:
            products = products.filter(category=category)
            selected_category_name = category.name

    feedbacks = Feedback.objects.order_by('-created_at')[:20]
    return render(request, 'products.html', {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category_slug,
        'selected_category_name': selected_category_name,
        'feedbacks': feedbacks,
        'is_staff': getattr(request.user, 'is_staff', False),
    })


def category(request):
    """
    Category listing page and staff-only creation form.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated or not request.user.is_staff:
            messages.error(request, 'Only staff users can create categories.')
            return redirect('category')
        name = request.POST.get('name', '').strip()
        image = request.FILES.get('image')

        if not name:
            messages.error(request, 'Category name is required.')
            return redirect('category')

        if Category.objects.filter(name__iexact=name).exists():
            messages.error(request, 'A category with this name already exists.')
            return redirect('category')

        if not image:
            messages.error(request, 'Category image is required.')
            return redirect('category')

        base_slug = slugify(name)
        slug = base_slug
        counter = 1
        while Category.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{counter}'
            counter += 1

        Category.objects.create(name=name, slug=slug, image=image)
        messages.success(request, f'Category "{name}" created successfully.')
        return redirect('category')

    categories = Category.objects.annotate(product_count=Count('products'))
    return render(request, 'category.html', {'categories': categories})


def product_detail(request, slug):
    """
    Product detail page.
    """
    product = get_object_or_404(Product, slug=slug)
    in_cart = False
    in_wishlist = False
    if request.user.is_authenticated:
        in_cart = CartItem.objects.filter(user=request.user, product=product).exists()
        in_wishlist = WishlistItem.objects.filter(user=request.user, product=product).exists()

    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    all_categories = Category.objects.all()
    featured_products = Product.objects.exclude(id=product.id)[:6]
    
    return render(request, 'product_detail.html', {
        'product': product,
        'in_cart': in_cart,
        'in_wishlist': in_wishlist,
        'related_products': related_products,
        'all_categories': all_categories,
        'featured_products': featured_products,
    })


@login_required(login_url='login')
def cart(request):
    """
    Shopping cart page.
    """
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    cart_total = sum(item.total_price for item in cart_items)
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
    })


@login_required(login_url='login')
def add_to_cart(request, slug):
    """
    Add a product to the cart.
    """
    product = get_object_or_404(Product, slug=slug)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity = min(cart_item.quantity + 1, 10)
        cart_item.save()
        messages.success(request, f'Updated quantity for {product.title} in your cart.')
    else:
        messages.success(request, f'Added {product.title} to your cart.')
    return redirect('product_detail', slug=slug)


@login_required(login_url='login')
def remove_from_cart(request, slug):
    """
    Remove a product from the cart.
    """
    product = get_object_or_404(Product, slug=slug)
    CartItem.objects.filter(user=request.user, product=product).delete()
    messages.success(request, f'Removed {product.title} from your cart.')
    return redirect('cart')


@login_required(login_url='login')
def update_cart_quantity(request, slug):
    """
    Update quantity of a product in the cart.
    """
    if request.method == 'POST':
        product = get_object_or_404(Product, slug=slug)
        quantity = int(request.POST.get('quantity', 1))
        
        # Validate quantity
        if quantity < 1:
            quantity = 1
        elif quantity > 10:
            quantity = 10
        
        cart_item = get_object_or_404(CartItem, user=request.user, product=product)
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, f'Updated quantity for {product.title}.')
    
    return redirect('cart')


@login_required(login_url='login')
def wishlist(request):
    """
    Wishlist page.
    """
    items = WishlistItem.objects.filter(user=request.user).select_related('product')
    return render(request, 'wishlist.html', {'items': items})


@login_required(login_url='login')
def add_to_wishlist(request, slug):
    """
    Add a product to the wishlist.
    """
    product = get_object_or_404(Product, slug=slug)
    wishlist_item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
    if created:
        messages.success(request, f'Added {product.title} to your wishlist.')
    else:
        messages.info(request, f'{product.title} is already in your wishlist.')
    return redirect('product_detail', slug=slug)


@login_required(login_url='login')
def remove_from_wishlist(request, slug):
    """
    Remove an item from the wishlist.
    """
    product = get_object_or_404(Product, slug=slug)
    WishlistItem.objects.filter(user=request.user, product=product).delete()
    messages.success(request, f'Removed {product.title} from your wishlist.')
    return redirect('wishlist')


@login_required(login_url='login')
def checkout(request):
    """
    Checkout page - show address confirmation before creating order.
    """
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    if not cart_items:
        messages.warning(request, 'Your cart is empty. Add items before checkout.')
        return redirect('cart')

    cart_total = sum(item.total_price for item in cart_items)
    user = request.user
    
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'user': user,
    }
    
    return render(request, 'checkout.html', context)


@login_required(login_url='login')
@require_POST
def confirm_checkout(request):
    """
    Confirm checkout and create a pending order with Razorpay payment initialization.
    """
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    if not cart_items:
        if request.META.get('HTTP_X_REQUESTED_WITH', '').lower() == 'xmlhttprequest':
            return JsonResponse({'success': False, 'message': 'Your cart is empty.'}, status=400)
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')

    if request.POST.get('accept_terms') != 'on':
        if request.META.get('HTTP_X_REQUESTED_WITH', '').lower() == 'xmlhttprequest':
            return JsonResponse({'success': False, 'message': 'Please accept the Terms & Conditions before placing your order.'}, status=400)
        messages.error(request, 'Please accept the Terms & Conditions before placing your order.')
        return redirect('checkout')

    shipping_name = request.POST.get('shipping_name', request.user.full_name)
    shipping_address = request.POST.get('shipping_address', '').strip()
    shipping_phone = request.POST.get('shipping_phone', '').strip()
    use_saved_address = request.POST.get('use_saved_address') == 'on'

    if use_saved_address:
        shipping_address = request.user.address or ''
        shipping_phone = request.user.mobile or ''

    if not shipping_address or not shipping_phone:
        error_message = 'Please provide a phone number.' if not shipping_phone else 'Please provide a shipping address.'
        if request.META.get('HTTP_X_REQUESTED_WITH', '').lower() == 'xmlhttprequest':
            return JsonResponse({'success': False, 'message': error_message}, status=400)
        messages.error(request, error_message)
        return redirect('checkout')

    total = sum(item.total_price for item in cart_items)
    amount_paise = int(Decimal(total) * Decimal('100'))
    razorpay_order = create_razorpay_order(
        amount_paise,
        receipt=f'order_{request.user.id}_{int(datetime.utcnow().timestamp())}'
    )

    if not razorpay_order or razorpay_order.get('error'):
        error_message = razorpay_order.get('error') if isinstance(razorpay_order, dict) else None
        if request.META.get('HTTP_X_REQUESTED_WITH', '').lower() == 'xmlhttprequest':
            return JsonResponse({
                'success': False,
                'message': f'Unable to initialize payment. {error_message or "Please try again."}'
            }, status=500)
        messages.error(request, f'Unable to initialize payment. {error_message or "Please try again."}')
        return redirect('checkout')

    order = Order.objects.create(
        user=request.user,
        total_price=Decimal(total),
        shipping_name=shipping_name,
        shipping_address=shipping_address,
        shipping_phone=shipping_phone,
        status='pending'
    )

    order_items = []
    for item in cart_items:
        order_items.append(OrderItem(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        ))
    OrderItem.objects.bulk_create(order_items)
    cart_items.delete()

    response_payload = {
        'success': True,
        'razorpay_key': settings.RAZORPAY_API_KEY,
        'razorpay_order_id': razorpay_order.get('id'),
        'amount': amount_paise,
        'currency': 'INR',
        'order_number': order.order_number,
        'local_order_id': order.id,
    }

    if request.META.get('HTTP_X_REQUESTED_WITH', '').lower() == 'xmlhttprequest':
        return JsonResponse(response_payload)

    return render(request, 'razorpay_checkout.html', response_payload)


def create_razorpay_order(amount, receipt):
    """Create a Razorpay order using the Razorpay REST API."""
    try:
        data = json.dumps({
            'amount': amount,
            'currency': 'INR',
            'receipt': receipt,
            'payment_capture': 1,
        }).encode()

        request_obj = urllib.request.Request(
            'https://api.razorpay.com/v1/orders',
            data=data,
            headers={'Content-Type': 'application/json'},
        )

        auth_string = f"{settings.RAZORPAY_API_KEY}:{settings.RAZORPAY_API_SECRET}"
        auth_header = base64.b64encode(auth_string.encode()).decode()
        request_obj.add_header('Authorization', f'Basic {auth_header}')

        with urllib.request.urlopen(request_obj, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode()
        except Exception:
            body = str(exc)
        return {'error': f'Razorpay HTTP {exc.code}: {body}'}
    except Exception as exc:
        return {'error': str(exc)}


@login_required(login_url='login')
@require_POST
def verify_payment(request):
    """Verify Razorpay payment signature and complete the order."""
    try:
        data = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'success': False, 'message': 'Invalid payment payload.'}, status=400)

    payment_id = data.get('razorpay_payment_id')
    razorpay_order_id = data.get('razorpay_order_id')
    signature = data.get('razorpay_signature')
    local_order_id = data.get('local_order_id')

    if not all([payment_id, razorpay_order_id, signature, local_order_id]):
        return JsonResponse({'success': False, 'message': 'Missing payment details.'}, status=400)

    order = get_object_or_404(Order, id=local_order_id, user=request.user)
    expected_signature = hmac.new(
        settings.RAZORPAY_API_SECRET.encode(),
        f"{razorpay_order_id}|{payment_id}".encode(),
        hashlib.sha256,
    ).hexdigest()

    if signature != expected_signature:
        return JsonResponse({'success': False, 'message': 'Payment verification failed.'}, status=400)

    order.status = 'completed'
    order.razorpay_order_id = razorpay_order_id
    order.razorpay_payment_id = payment_id
    order.save(update_fields=['status', 'razorpay_order_id', 'razorpay_payment_id', 'updated_at'])

    return JsonResponse({'success': True, 'redirect_url': reverse('order_success', args=[order.id])})


@login_required(login_url='login')
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status != 'completed':
        messages.warning(request, 'Payment is not completed for this order yet.')
        return redirect('orders')

    return render(request, 'order_success.html', {'order': order})


@login_required(login_url='login')
def orders(request):
    """
    My Orders page (requires login).
    """
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    return render(request, 'orders.html', {'orders': orders})


@login_required(login_url='login')
def cancel_order(request, order_id):
    """
    Display order cancellation form with reason selection.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if order can be cancelled (only pending orders)
    if order.status != 'pending':
        messages.error(request, 'Only pending orders can be cancelled.')
        return redirect('orders')
    
    cancellation_reasons = Order.CANCELLATION_REASONS
    return render(request, 'cancel_order.html', {
        'order': order,
        'cancellation_reasons': cancellation_reasons,
    })


@login_required(login_url='login')
def confirm_cancel_order(request, order_id):
    """
    Process order cancellation with reason.
    """
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Check if order can be cancelled
        if order.status != 'pending':
            messages.error(request, 'Only pending orders can be cancelled.')
            return redirect('orders')
        
        # Get cancellation reason and message
        reason = request.POST.get('cancellation_reason', '').strip()
        message = request.POST.get('cancellation_message', '').strip()
        
        # Validate reason is selected
        valid_reasons = [choice[0] for choice in Order.CANCELLATION_REASONS]
        if reason not in valid_reasons:
            messages.error(request, 'Please select a valid cancellation reason.')
            return redirect('cancel_order', order_id=order_id)
        
        # Validate message if "other" is selected
        if reason == 'other' and not message:
            messages.error(request, 'Please provide a reason for cancellation.')
            return redirect('cancel_order', order_id=order_id)
        
        # Update order status
        order.status = 'cancelled'
        order.cancellation_reason = reason
        order.cancellation_message = message if message else None
        order.cancelled_at = datetime.now()
        order.save()
        
        messages.success(request, f'Order #{order.id} has been cancelled successfully.')
        return redirect('orders')
    
    return redirect('orders')


def contact(request):
    """
    Contact page.
    """
    if request.method == 'POST':
        # For now simply acknowledge and redirect back
        messages.success(request, 'Thanks for contacting us. We will get back to you soon.')
        return redirect('contact')
    return render(request, 'contact.html')


@login_required(login_url='login')
def support(request):
    """
    Support page.
    """
    return render(request, 'support.html')


@require_POST
def submit_feedback(request):
    """Handle feedback submissions from the products page."""
    comment = request.POST.get('comment', '').strip()
    full_name = request.POST.get('full_name', '').strip()
    rating = int(request.POST.get('rating') or 0)
    profile_image = request.FILES.get('profile_image')

    # enforce 500-word limit
    word_count = len(comment.split())
    if word_count > 500:
        messages.error(request, f'Feedback is too long ({word_count} words). Limit is 500 words.')
        return redirect('products')

    feedback = Feedback.objects.create(
        user=request.user if request.user.is_authenticated else None,
        full_name=full_name or (request.user.full_name if request.user.is_authenticated else 'Anonymous'),
        rating=max(1, min(5, rating)),
        comment=comment,
    )

    if profile_image:
        feedback.profile_image.save(profile_image.name, profile_image)

    messages.success(request, 'Thank you for your feedback!')
    return redirect('products')

