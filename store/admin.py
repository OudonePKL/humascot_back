from django.contrib import admin

from .models import (
    StoreModel,
    OrderModel,
    ReviewModel,
    CategoryModel,
    ImageModel,
    GoodsModel,
    FilteringModel, PolicyModel,
    Cart, CartItem,
    Bill, BillItem, 
    Payment
)


@admin.register(StoreModel)
class StoreAdmin(admin.ModelAdmin):

    """Board Admin Definition"""

    list_display = (
        "name",
        "seller",
        "address",
    )

    search_fields = (
        "name",
        "seller",
    )


@admin.register(CategoryModel)
class CategoryAdmin(admin.ModelAdmin):

    """Board Admin Definition"""

    list_display = ("name",)

    search_fields = ("name",)


@admin.register(GoodsModel)
class GoodsAdmin(admin.ModelAdmin):

    """Board Admin Definition"""

    list_display = (
        "category",
        "store",
        "name",
        "price",
    )

    search_fields = ("name", "store")

    list_filter = ("category",)


@admin.register(OrderModel)
class OrderAdmin(admin.ModelAdmin):

    """Board Admin Definition"""

    list_display = ("goods", "price", "user", "ordered_at")

    search_fields = ("user", "goods")


@admin.register(ReviewModel)
class ReviewModelAdmin(admin.ModelAdmin):
    list_display = ("goods", "user", "star")

    search_fields = ("user", "goods")

    list_filter = ("star",)


@admin.register(ImageModel)
class ImageModelAdmin(admin.ModelAdmin):

    """Board Admin Definition"""

    list_display = ("goods", "image")

    search_fields = ("goods",)


@admin.register(FilteringModel)
class FilteringModelAdmin(admin.ModelAdmin):

    """Board Admin Definition"""

    list_display = ("id", "filter", "option")
    list_display_links = ("filter", "option")

    search_fields = ("filtering",)


@admin.register(PolicyModel)
class FilteringModelAdmin(admin.ModelAdmin):

    """Board Admin Definition"""

    list_display = ("id","category")
    list_display_links = ("category",)

    search_fields = ("category",)

@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ("id", "store_id", "user_id")
    search_fields = ("user_id", "store_id")

@admin.register(CartItem)
class CartItemModelAdmin(admin.ModelAdmin):
    list_display = ("cart_id", "goods_id", "size", "color")
    search_fields = ("cart_id", "goods_id", "size", "color")

@admin.register(Bill)
class BillModelAdmin(admin.ModelAdmin):
    list_display = ("id", "store_id", "amount", "due_date")
    search_fields = ("id", "store_id")

@admin.register(BillItem)
class BillItemModelAdmin(admin.ModelAdmin):
    list_display = ("id", "bill_id", "goods_id", "quantity", "size", "color")
    search_fields = ("id", "bill_id",)

@admin.register(Payment)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display = ("id", "user_id", "bill_id", "amount", "payment_date", "status")
    search_fields = ("user_id", "bill_id")
