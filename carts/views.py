from django.shortcuts import redirect, render, get_object_or_404
from store.models import Product, Variation
from carts.models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id) # Get the product by ID

    # User Is Authenticated
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)  # Append the variation to the list
                except:
                    pass

        # Check if the product is already in the cart
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)  # Check if the item is already in the cart of the user
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variations = item.variations.all()
                ex_var_list.append(list(existing_variations))  # Get existing variations
                id.append(item.id)

            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)  # Get the index of the matching variations
                item_id = id[index]  # Get the corresponding item ID
                item = CartItem.objects.get(product=product, id=item_id)  # Get the cart item
                item.quantity += 1  # Increment the quantity if it exists
                item.save()

            else:
                item = CartItem.objects.create(
                    product=product,
                    quantity=1,
                    user=current_user
                )
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)  # Add variations to the cart item
                item.save()  # Save the updated cart item
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)  # Add variations to the cart item
            cart_item.save()
        return redirect('cart')
    
    # User Not Authenticated
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)  # Append the variation to the list
                except:
                    pass


        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) # Get the cart using the session key
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
        cart.save()  # Save the cart

        # Check if the product is already in the cart
        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)  # Check if the item is already in the cart
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variations = item.variations.all()
                ex_var_list.append(list(existing_variations))  # Get existing variations
                id.append(item.id)

            print(ex_var_list)

            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)  # Get the index of the matching variations
                item_id = id[index]  # Get the corresponding item ID
                item = CartItem.objects.get(product=product, cart=cart, id=item_id)  # Get the cart item
                item.quantity += 1  # Increment the quantity if it exists
                item.save()
            else:
                item = CartItem.objects.create(
                    product=product,
                    quantity=1,
                    cart=cart
                )
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)  # Add variations to the cart item
                item.save()  # Save the updated cart item
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)  # Add variations to the cart item
            cart_item.save()
        return redirect('cart')
    

def remove_cart(request, product_id, cart_item_id):    
    product = get_object_or_404(Product, id=product_id)  # Get the product by ID
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)  # Get the cart item
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))  # Get the cart using the session key
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)  # Get the cart item
        if cart_item.quantity > 1:
            cart_item.quantity -= 1  # Decrement the quantity if more than 1
            cart_item.save()  # Save the updated cart item
        else:
            cart_item.delete()  # Remove the item from the cart if quantity is 1
    except:
        pass
    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):    
    product = get_object_or_404(Product, id=product_id)  # Get the product by ID
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)  # Get the cart item by user
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))  # Get the cart using the session key
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)  # Get the cart item
    cart_item.delete()  # Remove the item from the cart
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        delivery_charge = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)  # Get all active items in the cart of the user
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))  # Get the cart using the session key
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)  # Get all active items in the cart
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)  # Calculate total price
            quantity += cart_item.quantity  # Calculate total quantity
        delivery_charge = 25  # Set delivery charge to 25
        grand_total = total + delivery_charge  # Calculate grand total
    except Cart.DoesNotExist:
        pass  # If no cart exists, we simply pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'grand_total': grand_total,
        'delivery_charge': delivery_charge
    }
    return render(request, 'store/cart.html', context)


@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        delivery_charge = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)  # Get all active items in the cart of the user
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))  # Get the cart using the session key
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)  # Get all active items in the cart
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)  # Calculate total price
            quantity += cart_item.quantity  # Calculate total quantity
        delivery_charge = 25  # Set delivery charge to 25
        grand_total = total + delivery_charge  # Calculate grand total
    except Cart.DoesNotExist:
        pass  # If no cart exists, we simply pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'grand_total': grand_total,
        'delivery_charge': delivery_charge
    }
    return render(request, 'store/checkout.html', context)