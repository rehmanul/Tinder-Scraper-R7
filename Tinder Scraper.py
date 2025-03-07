from django.db import models from django.contrib.auth.models import User from django.db.models.signals import post_save from django.dispatch import receiver from django.utils import timezone from django.core.validators import MaxValueValidator, MinValueValidator

Create your models here.
class Profile(models.Model): user = models.OneToOneField(User, on_delete=models.CASCADE) first_name = models.CharField(max_length=30, blank=True) last_name = models.CharField(max_length=30, blank=True) email = models.EmailField(max_length=254, blank=True) birth_date = models.DateField(null=True, blank=True) bio = models.TextField(max_length=500, blank=True) location = models.CharField(max_length=30, blank=True) phone = models.CharField(max_length=30, blank=True) avatar = models.ImageField(upload_to='avatars/', null=True, blank=True) created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True)

Run
Copy code
def __str__(self):
    return self.user.username
@receiver(post_save, sender=User) def create_user_profile(sender, instance, created, **kwargs): if created: Profile.objects.create(user=instance)

@receiver(post_save, sender=User) def save_user_profile(sender, instance, **kwargs): instance.profile.save()

class Category(models.Model): name = models.CharField(max_length=30, unique=True) description = models.TextField(max_length=500, blank=True) created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True)

Run
Copy code
def __str__(self):
    return self.name
class Product(models.Model): name = models.CharField(max_length=30) description = models.TextField(max_length=500, blank=True) price = models.DecimalField(max_digits=10, decimal_places=2) category = models.ForeignKey(Category, on_delete=models.CASCADE) image = models.ImageField(upload_to='products/', null=True, blank=True) stock = models.PositiveIntegerField(default=0) available = models.BooleanField(default=True) created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True)

Run
Copy code
def __str__(self):
    return self.name
class Order(models.Model): user = models.ForeignKey(User, on_delete=models.CASCADE) products = models.ManyToManyField(Product, through='OrderItem') total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0) created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True) status = models.CharField(max_length=30, default='pending') shipping_address = models.TextField(max_length=500, blank=True) payment_method = models.CharField(max_length=30, blank=True) payment_status = models.CharField(max_length=30, default='pending') delivery_date = models.DateTimeField(null=True, blank=True)

Run
Copy code
def __str__(self):
    return f'Order {self.id} by {self.user.username}'
class OrderItem(models.Model): order = models.ForeignKey(Order, on_delete=models.CASCADE) product = models.ForeignKey(Product, on_delete=models.CASCADE) quantity = models.PositiveIntegerField(default=1) price = models.DecimalField(max_digits=10, decimal_places=2)

Run
Copy code
def __str__(self):
    return f'{self.quantity} of {self.product.name} in order {self.order.id}'
class Review(models.Model): user = models.ForeignKey(User, on_delete=models.CASCADE) product = models.ForeignKey(Product, on_delete=models.CASCADE) rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)]) comment = models.TextField(max_length=500, blank=True) created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True)

Run
Copy code
def __str__(self):
    return f'Review by {self.user.username} for {self.product.name}'
class Cart(models.Model): user = models.OneToOneField(User, on_delete=models.CASCADE) products = models.ManyToManyField(Product, through='CartItem') created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True)

Run
Copy code
def __str__(self):
    return f'Cart of {self.user.username}'
class CartItem(models.Model): cart = models.ForeignKey(Cart, on_delete=models.CASCADE) product = models.ForeignKey(Product, on_delete=models.CASCADE) quantity = models.PositiveIntegerField(default=1)

Run
Copy code
def __str__(self):
    return f'{self.quantity} of {self.product.name} in cart {self.cart.id}'
class Wishlist(models.Model): user = models.OneToOneField(User, on_delete=models.CASCADE) products = models.ManyToManyField(Product) created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True)

Run
Copy code
def __str__(self):
    return f'Wishlist of {self.user.username}'
class Coupon(models.Model): code = models.CharField(max_length=30, unique=True) discount = models.DecimalField(max_digits=5, decimal_places=2) valid_from = models.DateTimeField() valid_to = models.DateTimeField() active = models.BooleanField(default=True) created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True)

Run
Copy code
def __str__(self):
    return self.code
class Payment(models.Model): order = models.ForeignKey(Order, on_delete=models.CASCADE) amount = models.DecimalField(max_digits=10, decimal_places=2) payment_method = models.CharField(max_length=30) transaction_id = models.CharField(max_length=100) status = models.CharField(max_length=30) created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True)

Run
Copy code
def __str__(self):
    return f'Payment {self.transaction_id} for order {self.order.id}'
class Shipping(models.Model): order = models.ForeignKey(Order, on_delete=models.CASCADE) address = models.TextField(max_length=500) city = models.CharField(max_length=30) state = models.CharField(max_length=30) country = models.CharField(max_length=30) postal_code = models.CharField(max_length=30) tracking_number = models.CharField(max_length=100, blank=True) status = models.CharField(max_length=30, default='pending') created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True)

Run
Copy code
def __str__(self):
    return f'Shipping for order {self.order.id} to {self.city}'
class Contact(models.Model): user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) name = models.CharField(max_length=30) email = models.EmailField(max_length=254) subject = models.CharField(max_length=100) message = models.TextField(max_length=500) created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True)

Run
Copy code
def __str__(self):
    return f'Message from {self.name} about {self.subject}'
class Newsletter(models.Model): email = models.EmailField(max_length=254, unique=True) subscribed = models.BooleanField(default=True) created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True)

Run
Copy code
def __str__(self):
    return self.email
class Blog(models.Model): title = models.CharField(max_length=100) content = models.TextField(max_length=5000) author = models.ForeignKey(User, on_delete=models.CASCADE) image = models.ImageField(upload_to='blogs/', null=True, blank=True) created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True) published = models.BooleanField(default=False) published_at = models.DateTimeField(null=True, blank=True)

Run
Copy code
def __str__(self):
    return self.title
class Comment(models.Model): blog = models.ForeignKey(Blog, on_delete=models.CASCADE) user = models.ForeignKey(User, on_delete=models.CASCADE) content = models.TextField(max_length=500) created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True) approved = models.BooleanField(default=False)

Run
Copy code
def __str__(self):
    return f'Comment by {self.user.username} on {self.blog.title}'
class Tag(models.Model): name = models.CharField(max_length=30, unique=True) blogs = models.ManyToManyField(Blog) created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True)

Run
Copy code
def __str__(self):
    return self.name
class FAQ(models.Model): question = models.CharField(max_length=200) answer = models.TextField(max_length=500) created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True) active = models.BooleanField(default=True)

Run
Copy code
def __str__(self):
    return self.question
class SiteSetting(models.Model): name = models.CharField(max_length=30, unique=True) value = models.TextField(max_length=500) created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True)

Run
Copy code
def __str__(self):
    return self.name
class Page(models.Model): title = models.CharField(max_length=100) slug = models.SlugField(max_length=100, unique=True) content = models.TextField(max_length=5000) created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True) published = models.BooleanField(default=False) published_at = models.DateTimeField(null=True, blank=True)

Run
Copy code
def __str__(self):
    return self.title
class Banner(models.Model): title = models.CharField(max_length=100) image = models.ImageField(upload_to='banners/') link = models.URLField(max_length=200, blank=True) active = models.BooleanField(default=True) created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True)

Run
Copy code
def __str__(self):
    return self.title
class Notification(models.Model): user = models.ForeignKey(User, on_delete=models.CASCADE) message = models.TextField(max_length=500) read = models.BooleanField(default=False) created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True)

Run
Copy code
def __str__(self):
    return f'Notification for {self.user.username}'
class Report(models.Model): user = models.ForeignKey(User, on_delete=models.CASCADE) title = models.CharField(max_length=100) content = models.TextField(max_length=500) created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True) resolved = models.BooleanField(default=False)

Run
Copy code
def __str__(self):
    return self.title
class ActivityLog(models.Model): user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) action = models.CharField(max_length=100) details = models.TextField(max_length=500) created_at = models.DateTimeField(auto_now_add=True)

Run
Copy code
def __str__(self):
    return f'{self.action} by {self.user.username if self.user else "System"}'
class Subscription(models.Model): user = models.ForeignKey(User, on_delete=models.CASCADE) plan = models.CharField(max_length=30) start_date = models.DateTimeField() end_date = models.DateTimeField() active = models.BooleanField(default=True) created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True)

Run
Copy code
def __str__(self):
    return f'Subscription of {self.user.username} to {self.plan}'
class Invoice(models.Model): user = models.ForeignKey(User, on_delete=models.CASCADE) amount = models.DecimalField(max_digits=10, decimal_places=2) date = models.DateTimeField(auto_now_add=True) due_date = models.DateTimeField() paid = models.BooleanField(default=False) created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True)

Run
Copy code
def __str__(self):
    return f'Invoice {self.id} for {self.user.username}'
class SupportTicket(models.Model): user = models.ForeignKey(User, on_delete=models.CASCADE) subject = models.CharField(max_length=100) message = models.TextField(max_length=500) status = models.CharField(max_length=30, default='open') created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True)

Run
Copy code
def __str__(self):
    return f'Ticket {self.id} by {self.user.username}'
class TicketReply(models.Model): ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE) user = models.ForeignKey(User, on_delete=models.CASCADE) message = models.TextField(max_length=500) created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True)

Run
Copy code
def __str__(self):
    return f'Reply to ticket {self.ticket.id} by {self.user.username}'
class SocialAccount(models.Model): user = models.ForeignKey(User, on_delete=models.CASCADE) provider = models.CharField(max_length=30) uid = models.CharField(max_length=200) extra_data = models.JSONField() created_at = models.DateTimeField(auto_now_add=True) updated_at = models.DateTimeField(auto_now=True)

Run
Copy code
def __str__(self):
    return f'{self.provider} account for {self.user.username}'
class APIKey(models.Model): user = models.ForeignKey(User, on_delete=models.CASCADE) key = models.CharField(max_length=100, unique=True) name = models.CharField(max_length=30) active = models.Boolean