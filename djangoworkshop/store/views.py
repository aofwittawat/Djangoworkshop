from django.shortcuts import render
from store.models import Category, Product


def index(request):
    products = None
    products = Product.objects.all().filter(available=True)
    return render(request, 'index.html', {'products': products})


def product(request):
    return render(request, 'product.html')
