from django.contrib import admin
from django.urls import path
from store import views
# import รูปมาใส่ ใน static folder
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),
    path('category/<slug:category_slug>',
         views.index, name="product_by_category"),
    path('product/<slug:category_slug>/<slug:product_slug>',
         views.productPage, name='productDetail'),
    path('cart/add/<int:product_id>', views.addCart, name='addCart'),
    path('cartdetail', views.cartdetail, name='cartdetail'),
    path('cart/remove/<int:product_id>', views.removeCart, name='removeCart'),
    path('account/create', views.signupView, name='signup'),
    path('account/login', views.signInview, name='signin'),
    path('account/logout', views.signOutview, name='signout'),
    path('search/', views.search, name='search'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
