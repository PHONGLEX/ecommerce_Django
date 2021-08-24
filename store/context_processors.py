from django.shortcuts import get_object_or_404
from .models import Order

import json


def cart_number(request):
	try:
		if request.user.is_authenticated:
			customer = request.user.customer
			order = get_object_or_404(Order, customer=customer, complete=False)

			return {
				'number_of_items': order.get_cart_items
			}
		else:
			number_of_items = 0
			try:
				cart = json.loads(request.COOKIES['cart'])
			except Exception as e:
				cart = {}

			for i in cart:
				number_of_items += cart[i] ['quantity']

			return {
				'number_of_items': number_of_items
			}
	except Exception as e:
		return {
			'number_of_items': 0
		}