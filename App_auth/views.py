import random
from django.shortcuts import render, HttpResponseRedirect, reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from App_auth.forms import *
from App_auth.models import *


# Create your views here.
def is_customer(user):
    return user.groups.filter(name="CUSTOMER").exists()


def login_view(request):
    login_form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect(reverse('home'))
    content = {
        'login_form': login_form,
    }
    return render(request, 'login_view.html', context=content)


def register_view(request):
    signupForm = SignupForm()
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            my_admin_group = Group.objects.get_or_create(name='CUSTOMER')
            my_admin_group[0].user_set.add(user)
            return HttpResponseRedirect(reverse('App_auth:login'))
    content =  {
        'signupForm': signupForm,
    }
    return render(request, 'register_view.html', context=content)


# Customer Page
def customer_dashboard(request):
    c = Cart.objects.filter(user=request.user)
    products = ProductModel.objects.all()
    total_cart = Cart.objects.filter(user=request.user, purchased=False)
    cart_prod = [x.item.product_name for x in total_cart]
    content = {
        'products': products,
        'cart': total_cart,
        'prod_name': cart_prod
    }
    return render(request, 'customer_dashboard.html', context=content)


def add_to_cart(request):
    pk = request.POST.get('product_id')
    quantity = int(request.POST.get('product_asking_quantity'))
    prod = ProductModel.objects.get(id=pk)
    try:
        cart_item = Cart.objects.get(user=request.user, item=prod, purchased=False)
        cart_item.quantity += quantity
        cart_item.save()
    except:
        cart_item = Cart.objects.create(user=request.user, item=prod, quantity=quantity, purchased=False)
        cart_item.save()
    return HttpResponseRedirect(reverse('home'))



def cart_showcase(request):
    carts = Cart.objects.filter(user=request.user, purchased=False)
    complete_order = Order.objects.filter(user=request.user, status='Completed')
    total_order = Order.objects.filter(user=request.user)
    if not total_order.exists():
        no_order = True
    else:
        no_order = False
    
    if complete_order.count() == total_order.count():
        all_order_completed = True
    else:
        all_order_completed = False

    if len(carts) == 0:
        return HttpResponseRedirect(reverse('home'))
    content = {
        'carts': carts,
        'all_order_completed': all_order_completed,
        'no_order': no_order,
    }
    return render(request, 'cartView.html', context=content)


def cart_update(request):
    pk = request.POST.get('product_id')
    prod = ProductModel.objects.get(id=pk)
    quantity = request.POST.get('new_asking_quantity')
    if quantity == "" or int(quantity) == 0:
        cart_item = Cart.objects.get(user=request.user, item=prod, purchased=False)
        cart_item.delete()
        return HttpResponseRedirect(reverse('App_auth:cart-view'))
    else:
        quantity = int(quantity)
    cart_item = Cart.objects.get(user=request.user, item=prod, purchased=False)
    cart_item.quantity = quantity
    cart_item.save()
    return HttpResponseRedirect(reverse('App_auth:cart-view'))


def remove_item_from_cart(request, itemID):
    product = ProductModel.objects.get(id=itemID)
    cart_item = Cart.objects.get(user=request.user, item=product, purchased=False)
    cart_item.delete()
    return HttpResponseRedirect(reverse('App_auth:cart-view'))


def total_price_count(List, total):
    if len(List) == 0:
        return total
    else:
        i = List[0]
        total += i.quantity * i.item.price_per_unit
        List.remove(i)
        return total_price_count(List, total)


def checkout(request):
    saved_address = BillingAddress.objects.get_or_create(user=request.user)
    saved_address = saved_address[0]
    form = BillingForm(instance=saved_address)
    if request.method == "POST":
        form = BillingForm(request.POST, instance=saved_address)
        if form.is_valid():
            form.save()
            form = BillingForm(instance=saved_address)

    cartItems = Cart.objects.filter(user=request.user, purchased=False)
    orderTotal = total_price_count(list(cartItems), 0)
    content = {
        'form': form,
        'cartItems': cartItems,
        'orderTotal': orderTotal,
        'saved_address': saved_address
    }
    return render(request, 'checkout.html', context=content)


def add_to_order(cart, order, total):
    if len(cart) == 0:
        return order
    else:
        i = cart[0]
        order.order_items.add(i)
        order.ordered = True
        order.payment_id = str(i.user)
        order.status = "Processing"
        order.order_id = str(i.user.id) + "-" + str(random.randint(1, 10000))
        order.total_price = total
        cart.remove(i)
        return add_to_order(cart, order, total)


def delete_list(l_Delete):
    if len(l_Delete) == 0:
        return 0
    else:
        l_Delete[0].delete()
        delete_list(l_Delete)


def purchase_action(request):
    order = Order.objects.create(user=request.user)
    cart_items = Cart.objects.filter(user=request.user, purchased=False)
    total = total_price_count(list(cart_items), 0)
    add_to_order(list(cart_items), order, total).save()
    for item in cart_items:
        # product = ProductModel.objects.get(id=item.item.id)
        # if product.No_of_available < item.quantity:
        #     shortage = ShortageOfProduct(product=product)
        #     storageAmount = item.quantity - product.No_of_available
        #     shortage.storageAmount = storageAmount
        #     shortage.save()
        #     product.No_of_available = 0
        # else:
        #     product.No_of_available -= item.quantity
        # product.save()
        item.purchased = True
        item.save()
        orderDelete = Order.objects.filter(user=request.user, payment_id=None)
        delete_list(orderDelete)

    return HttpResponseRedirect(reverse('home'))


def profile_view(request):
    profile = Profile.objects.get(user=request.user)
    form = ProfileForm(instance=profile)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            thisForm = form.save(commit=False)
            thisForm.user = request.user
            thisForm.save()
            return HttpResponseRedirect(reverse('App_auth:profile-view'))

    content = {
        'profile': profile,
        'form': form,
    }
    return render(request, 'profile_view.html', context=content)


def previous_orders(request):
    previous_order = Order.objects.filter(user=request.user)
    content = {
        'previous_orders': previous_order
    }
    return render(request, 'previous_orders.html', context=content)

def cart_update(request):
    pk = request.POST.get('product_id')
    prod = ProductModel.objects.get(id=pk)
    quantity = request.POST.get('new_asking_quantity')
    if quantity == "" or int(quantity) == 0:
        cart_item = Cart.objects.get(user=request.user, item=prod, purchased=False)
        cart_item.delete()
        return HttpResponseRedirect(reverse('App_auth:cart-view'))
    else:
        quantity = int(quantity)
    cart_item = Cart.objects.get(user=request.user, item=prod, purchased=False)
    cart_item.quantity = quantity
    cart_item.save()
    return HttpResponseRedirect(reverse('App_auth:cart-view'))


def remove_item_from_cart(request, itemID):
    product = ProductModel.objects.get(id=itemID)
    cart_item = Cart.objects.get(user=request.user, item=product, purchased=False)
    cart_item.delete()
    return HttpResponseRedirect(reverse('App_auth:cart-view'))


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('App_auth:login'))

