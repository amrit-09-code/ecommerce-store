from django.shortcuts import render, redirect
from .models import Product, Category, Customer


def get_cart_data(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    count = 0

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue

        subtotal = product.price * quantity
        total += subtotal
        count += quantity
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    return {
        'items': cart_items,
        'total': total,
        'count': count,
    }


def home(request):
    categories = Category.objects.all()
    cat_id = request.GET.get('category')
    if cat_id:
        products = Product.objects.filter(category_id=cat_id)
    else:
        products = Product.objects.all()

    cart_data = get_cart_data(request)
    return render(
        request,
        'store/home.html',
        {
            'products': products,
            'categories': categories,
            'cart_count': cart_data['count'],
            'selected_category': cat_id,
        }
    )


def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    return redirect('cart')


def cart_view(request):
    cart_data = get_cart_data(request)
    return render(request, 'store/cart.html', {
        'cart_items': cart_data['items'],
        'total_amount': cart_data['total'],
        'cart_count': cart_data['count'],
    })


def signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not first_name or not last_name or not phone or not email or not password:
            return render(request, 'store/signup.html', {'error': 'All fields are required.'})

        if Customer.objects.filter(email=email).exists():
            return render(request, 'store/signup.html', {'error': 'This email is already registered.'})

        customer = Customer.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email,
            password=password,
        )
        request.session['customer_id'] = customer.id
        return redirect('home')

    return render(request, 'store/signup.html')


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        customer = Customer.objects.filter(email=email, password=password).first()
        if customer:
            request.session['customer_id'] = customer.id
            return redirect('home')
        return render(request, 'store/login.html', {'error': 'Invalid email or password.'})

    return render(request, 'store/login.html')


def logout(request):
    request.session.clear()
    return redirect('home')