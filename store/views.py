from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

from .models import Product, Order, OrderItem, ShippingAddress
from .decorators import prepare_context

import json
import datetime
from decimal import Decimal


def store(request):
	products = Product.objects.all()

	context = {
		"products": products
	}
	return render(request, "store/store.html", context)


@prepare_context
def cart(request, *args, **kwargs):
	context = kwargs.pop('context', {})	
	return render(request, "store/cart.html", context)


@prepare_context
def checkout(request, *args, **kwargs):
	context = kwargs.pop('context', {})
	return render(request, "store/checkout.html", context)


def updateItem(request):
	data = json.loads(request.body)

	productId = data.get('productId')
	action = data.get("action")

	customer = request.user.customer
	product = get_object_or_404(Product, id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)
	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == "add":
		orderItem.quantity += 1
	elif action == "remove":
		orderItem.quantity -= 1

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()	

	return JsonResponse({"success": "Item was added"})


def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		

		

	else:
		print("user is not logged in")

		name = data['form']['name']
		email = data['form']['email']
		items = kwargs.get("items")

		customer, created = Custom.objects.get_or_create(
			email=email,
		)
		customer.name = name
		customer.save()

		order = Order.objects.create(customer=customer, complete=False)

		for item in items:
			product = Product.objects.get(item['product']['id'])

			orderItem = OrderItem.objects.create(
				product=product,
				order=order,
				quantity=item['quantity']
			)

	total = Decimal(data['form']['total'])
	order.transaction_id = transaction_id
	
	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping:
		ShippingAddress.objects.create(
			customer=customer,
			order=order,
			address=data['shipping']['address'],
			city=data['shipping']['city'],
			state=data['shipping']['state'],
			zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse({"success": "Payment completed"})
