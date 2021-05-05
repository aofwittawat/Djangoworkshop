from django.core import paginator
from django.shortcuts import redirect, render, get_object_or_404
from store.models import Category, Product, Cart, CartItem
from store.form import SignUpForm
from django.contrib.auth.models import Group, User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.contrib.auth.decorators import login_required
from django.conf import settings
import stripe


def index(request, category_slug=None):
    products = None
    category_page = None
    if category_slug != None:
        category_page = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.all().filter(category=category_page,
                                                available=True)
    else:
        products = Product.objects.all().filter(available=True)
    paginator = Paginator(products, 3)
    try:
        page = int(request.GET.get('page', '1'))
    except:
        page = 1
    try:
        productperPage = paginator.page(page)
    except (EmptyPage, InvalidPage):
        productperPage = paginator.page(paginator.num_pages)
    return render(request, 'index.html', {'products': productperPage,
                                          'category': category_page})


def productPage(request, category_slug, product_slug):
    try:
        product = Product.objects.get(
            category__slug=category_slug, slug=product_slug)

    except Exception as e:
        raise e
    return render(request, 'product.html', {'product': product})

# สร้าง session เพื่อเก็บค่า


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

# การเรีกยใช้ Function addCart จะทำให้ได้ cart_id มาเก็บใน model Cart จะเรียก Function โดยการกดปุ่มที่หน้าเพจ


@login_required(login_url='/account/login')
def addCart(request, product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
            cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(product=product,
                                            cart=cart,
                                            quantity=1)
        cart_item.save()
    return redirect('/')


def cartdetail(request):
    total = 0
    counter = 0
    cart_items = None
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        for item in cart_items:
            total += (item.product.price * item.quantity)
            counter += item.quantity
    except Exception as e:
        pass
###################ชำระเงิน ผ่าน stripe ###############################################
    stripe.api_key = settings.SECRET_KEY
    stripe_total = int(total * 100)
    description = "Payment Online"
    data_key = settings.PUBLIC_KEY
    if request.method == "POST":
        try:
            token = request.POST['stripeToken']
            email = request.POST['stripeEmail']
            customer = stripe.Customer.create(
                email= email,
                source=token
            )
            charge = stripe.Charge.create(
                amount= stripe_total,
                currency = 'thb',
                description = description,
                customer = customer.id
            )
        except stripe.error.CardError as e:
            return False, e
####################################################################################
    return render(request, 'cartdetail.html', dict(cart_items=cart_items,
                                                   total=total,
                                                   counter=counter,
                                                   stripe_total=stripe_total,
                                                   data_key=data_key,
                                                   description=description))


def removeCart(request, product_id):
    # ทำงานกับตะกร้าสินค้า A
    cart = Cart.objects.get(cart_id=_cart_id(request))
    # ทำงานกับสินค้าที่จะลบว่ามีของอะไร ตาม product_id ที่ request เข้ามา 1
    product = get_object_or_404(Product, id=product_id)
    cartItem = CartItem.objects.get(product=product, cart=cart)
    # ลบรายการสินค้า ออกจากตะกร้า A
    cartItem.delete()
    return redirect('cartdetail')


def signupView(request):
    if request.method == 'POST':
        # เช็คว่าส่งมาแบบ POST
        form = SignUpForm(request.POST)
        # บันทึกข้อมูลมาแบบ valid ก่อน
        if form.is_valid():
            # บันทึกข้อมูล User
            form.save()
            # บันทึก group customer โดยดึง username มาใช้
            username = form.cleaned_data.get('username')
            # ดึงข้อมูลจาก User
            singup_user = User.objects.get(username=username)
            # จัดกลุ่ม
            customer_group = Group.objects.get(name='Customer')
            customer_group.user_set.add(singup_user)

    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def signInview(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                return redirect('signup')
    else:
        form = AuthenticationForm()
    return render(request, 'signin.html', {'form': form})


def signOutview(request):
    logout(request)
    return redirect('signin')


def search(request):
    # เก็บค่ามาใน name
    name = request.GET['title']
    products = Product.objects.filter(name__contains=name)
    return render(request, 'index.html', {'products': products})
