from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import order_created_celery

def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
        # очистить корзину
        cart.clear()
        order_created_celery.delay(order.id)
        request.session['order_id'] = order.id
        return redirect(reverse('orders:order_created'))
    else:
        form = OrderCreateForm()
    return render(request,'orders/order/create.html', {'cart': cart, 'form': form})

def order_created(request):
   return render(request, 'orders/order/created.html')

@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request,
    'admin/orders/order/detail.html',
    {'order': order})


# Create your views here.
