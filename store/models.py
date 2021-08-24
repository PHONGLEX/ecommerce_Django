from io import BytesIO
from PIL import Image

from django.db import models
from django.contrib.auth.models import User
from django.core.files import File


class Customer(models.Model):
	user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
	name = models.CharField(max_length=200, null=True)
	email = models.EmailField(max_length=200, null=True)

	class Meta:
		verbose_name = "Customer"
		verbose_name_plural = "Customers"

	def __str__(self):
		return self.name


class Product(models.Model):
	name = models.CharField(max_length=255, null=True)
	price = models.DecimalField(max_digits=6, decimal_places=2)
	digital = models.BooleanField(default=False, null=True, blank=True)
	image = models.ImageField(upload_to="images/", blank=True, null=True)
	thumbnail = models.ImageField(blank=True, null=True)

	class Meta:
		verbose_name = "Product"
		verbose_name_plural = "Products"

	def __str__(self):
		return self.name

	def get_thumbnail(self):
		if self.image:
			self.thumbnail = self.make_thumbnail(self.image)
			self.save()

			return self.thumbnail.url
		else:
			return "https://via.placeholder.com/240x180.jpg"

	def make_thumbnail(self, image, size=(300,200)):
		img = Image.open(image)
		img.convert('RGB')
		img.thumbnail(size)

		thumb_io = BytesIO()
		img.save(thumb_io, 'JPEG', quality=85)

		thumbnail = File(thumb_io, name=image.name)
		return thumbnail

	@property
	def thumbnailURL(self):
		return self.get_thumbnail()
	

class Order(models.Model):
	customer = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.SET_NULL)
	date_order = models.DateTimeField(auto_now_add=True)
	complete = models.BooleanField(default=False)
	transaction_id = models.CharField(max_length=255, null=True)

	class Meta:
		verbose_name = "Order"
		verbose_name_plural = "Orders"

	def __str__(self):
		return str(self.id)

	@property
	def get_cart_total(self):
		return sum((item.get_total) for item in self.items.all())

	@property
	def get_cart_items(self):
		return sum(item.quantity for item in self.items.all())

	@property
	def shipping(self):
		if self.items.filter(product__digital=True).exists():
			return True
		return False
	
	
	

class OrderItem(models.Model):
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
	order = models.ForeignKey(Order, related_name="items", on_delete=models.SET_NULL, blank=True, null=True)
	quantity = models.IntegerField(default=0, null=True, blank=True)
	date_added = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = "OrderItem"
		verbose_name_plural = "OrderItems"

	def __str__(self):
		return self.product.name

	@property
	def get_total(self):
		total = self.quantity * self.product.price
		return total
	
	

class ShippingAddress(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
	address = models.CharField(max_length=255)
	city = models.CharField(max_length=255)
	state = models.CharField(max_length=255)
	zipcode = models.CharField(max_length=255)
	date_added = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = "ShippingAddress"
		verbose_name_plural = "ShippingAddress"

	def __str__(self):
		return self.address
	