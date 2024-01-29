from django.db import models
from users.models import UserModel


class CategoryModel(models.Model):
    class Meta:
        db_table = "category"
        verbose_name_plural = "1. Category types"

    name = models.CharField(max_length=100, default="etc", verbose_name="Category name")

    def __str__(self):
        return str(self.name)


class StoreModel(models.Model):
    class Meta:
        db_table = "store"
        verbose_name_plural = "2. Store list"

    seller = models.ForeignKey(UserModel, on_delete=models.CASCADE, verbose_name="seller")
    name = models.CharField(max_length=100, verbose_name="Store name", )
    address = models.CharField(max_length=200, verbose_name="store location", )
    phone = models.CharField(max_length=200, null=True, blank=True)
    company_number = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Company Registration Number"
    )
    sub_address = models.CharField(max_length=200, verbose_name="Store detailed address", null=True, blank=True)
    introduce = models.TextField(null=True, blank=True, verbose_name="introduction")

    def __str__(self):
        return str(self.name)

class GoodsModel(models.Model):
    class Meta:
        db_table = "goods"
        verbose_name_plural = "3. Product list"

    store = models.ForeignKey(StoreModel, on_delete=models.CASCADE, verbose_name="store")
    category = models.ForeignKey(
        CategoryModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="category",
        default=1,
    )
    name = models.CharField(max_length=100, verbose_name="product name")
    price = models.PositiveIntegerField(default=0, verbose_name="price")
    description = models.TextField(null=True, blank=True, verbose_name="Product Description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)


class ImageModel(models.Model):
    class Meta:
        db_table = "image"
        verbose_name_plural = "4. Product image list"

    goods = models.ForeignKey(GoodsModel, on_delete=models.CASCADE, verbose_name="Goods")
    image = models.FileField(null=True, blank=True, verbose_name="image", upload_to="media/")
    image2 = models.FileField(null=True, blank=True, verbose_name="image2", upload_to="media/")

    def __str__(self):
        return str(self.goods.name)


class OrderModel(models.Model):
    class Meta:
        db_table = "order"
        verbose_name_plural = "5. Order History"

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, verbose_name="buyer")
    goods = models.ForeignKey(
        GoodsModel, on_delete=models.CASCADE, verbose_name="purchase goods"
    )
    price = models.PositiveIntegerField(default=0, verbose_name="price")
    ordered_at = models.DateTimeField(auto_now_add=True, verbose_name="order time")

    def __str__(self):
        return str(self.goods.name)


class ReviewModel(models.Model):
    class Meta:
        db_table = "review"
        verbose_name_plural = "6. Review history"

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, verbose_name="Writer")
    goods = models.ForeignKey(
        GoodsModel, on_delete=models.CASCADE, verbose_name="review product"
    )
    review = models.TextField()
    star = models.FloatField(default=0, verbose_name="scope")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.goods.name)


class BookmarkModel(models.Model):
    class Meta:
        db_table = "bookmark"
        verbose_name_plural = "Bookmark History"

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    goods = models.ForeignKey(GoodsModel, on_delete=models.CASCADE)
    bookmark = models.BooleanField(default=True)


class FilteringModel(models.Model):
    class Meta:
        verbose_name_plural = "7. Filter your product list"

    filter = models.CharField(max_length=100, verbose_name="filter")
    option = models.TextField(null=True, blank=True, default="", verbose_name="Additional explanation")


class PolicyModel(models.Model):
    class Meta:
        verbose_name_plural = "8. Terms and Privacy Policy"

    category = models.IntegerField(null=True, blank=True, default=1, verbose_name='type')
    content = models.TextField(null=True, blank=True, default='', verbose_name='detail')


class Cart(models.Model):
    class Meta:
        db_table = "cart"
        verbose_name_plural = "9. Cart list"

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    store = models.ForeignKey(StoreModel, on_delete=models.CASCADE)
    goods = models.ManyToManyField(GoodsModel, through='CartItem')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    class Meta:
        db_table = "Cart item"
        verbose_name_plural = "10. Cart item list"

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    goods = models.ForeignKey(GoodsModel, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)

class Bill(models.Model):
    class Meta:
        db_table = "Bill"
        verbose_name_plural = "11. Bill list"
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    store = models.ForeignKey(StoreModel, on_delete=models.CASCADE)
    items = models.ManyToManyField(GoodsModel, through='BillItem')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()

    def __str__(self):
        return f'{self.user.email} - {self.store.name} - {self.amount} - {self.due_date}'
    
class BillItem(models.Model):
    class Meta:
        db_table = "Bill Item"
        verbose_name_plural = "12. Bill item list"
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    goods = models.ForeignKey(GoodsModel, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    size = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f'{self.bill.user.email} - {self.goods.name} - {self.quantity} - {self.size} - {self.color}'

class Payment(models.Model):
    class Meta:
        db_table = "Payment"
        verbose_name_plural = "13. Payment list"
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
    ]

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f'{self.user.email} - {self.amount} - {self.payment_date} - {self.status}'


