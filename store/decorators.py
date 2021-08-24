from .models import Product, Order

import json


def prepare_context(func):
	def wrapper(request, *args, **kwargs):
		try:
			if request.user.is_authenticated:
				customer = request.user.customer
				order, created = Order.objects.get_or_create(customer=customer, complete=False)
				items = order.items.all()
			else:
				try:
					cart = json.loads(request.COOKIES['cart'])
				except Exception as e:
					cart = {}
				items = []
				order = {
					'get_cart_total': 0,
					'shipping': False
				}
				print(cart)
				for i in cart:
					try:
						product = Product.objects.get(id=i)
						total = product.price * cart[i]['quantity']
						order['get_cart_total'] += total
						print(product.thumbnail)
						item = {
							'product': {
								'id': product.id,
								'name': product.name,
								'price': product.price,
								'thumbnailURL': product.thumbnailURL
							},
							'quantity': cart[i]['quantity'],
							'get_total': total
						}
						print(item)
						items.append(item)

						if product.digital == False:
							order['shipping'] = True
					except:
						pass

			kwargs['context'] = {
				"items": items,
				"order": order
			}
		except Exception as e:
			pass
		return func(request, *args, **kwargs)
	return wrapper