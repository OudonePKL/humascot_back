import math
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from store.models import CategoryModel, StoreModel, GoodsModel, ReviewModel, OrderModel, ImageModel, Cart, CartItem, Bill, BillItem, Payment
from users.models import UserModel


def format_with_commas(n):
    return "{:,}".format(int(n))

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryModel
        fields = '__all__'


class GoodsSerializer(serializers.ModelSerializer):
    store_name = serializers.SerializerMethodField()
    star_avg = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    format_price = serializers.SerializerMethodField()
    review_total = serializers.SerializerMethodField()
    store_address = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def get_store_name(self, obj):
        store_name = obj.store.name
        if len(store_name) >= 7:
            store_name = f"{store_name[:7]}..."
        return store_name

    def get_star_avg(self, obj):
        review = ReviewModel.objects.filter(goods_id=obj.id).values("star")
        total = 0
        for i in review:
            total += i["star"]

        return math.ceil(total / review.count()) if total != 0 else 0

    def get_category(self, obj):
        return obj.category.name

    def get_format_price(self, obj):
        return str(format_with_commas(obj.price)) + 'one'

    def get_review_total(self, obj):
        review_total = ReviewModel.objects.filter(goods_id=obj.id).count()
        return review_total

    def get_store_address(self, obj):
        address = obj.store.address.split(' ')[:2]
        address = ' '.join(address)
        return address

    def get_image(self, obj):
        image = ImageModel.objects.filter(goods_id=obj.id).first()
        serializer = ImageSerializer(image)
        image = serializer.data.get("image")
        return image

    class Meta:
        model = GoodsModel
        exclude = ["created_at", "updated_at"]
        extra_kwargs = {
            "category": {"required": False},
        }


class UpdateStoreSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        name = attrs.get("name")
        if name:
            if len(name) > 15:
                raise ValidationError("Please write your store name in 15 characters or less.")
        return attrs

    class Meta:
        model = StoreModel
        fields = "__all__"
        extra_kwargs = {
            "seller": {"required": False},
        }


class OnlyStoreInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreModel
        exclude = ["seller"]


class StoreSerializer(serializers.ModelSerializer):
    goods_set = serializers.SerializerMethodField()

    class Meta:
        model = StoreModel
        fields = '__all__'

    # seller = serializers.SerializerMethodField()

    def get_seller(self, obj):
        return obj.seller.email

    def get_goods_set(self, obj):
        goods = GoodsModel.objects.filter(store_id=obj.id)
        serializer = OnlyStoreGoodsSerializer(goods, many=True)
        return serializer.data

    class Meta:
        model = StoreModel
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    nickname = serializers.SerializerMethodField()

    def validate(self, attrs):
        review = attrs.get("review")
        if review:
            if len(review) < 10:
                raise ValidationError("Please register your review with at least 10 characters.")
        return attrs

    def get_profile_image(self, obj):
        user = UserModel.objects.get(id=obj.user.id)
        if not user.profile_image:
            return None
        else:
            return user.profile_image.url

    def get_created_at(self, obj):
        return obj.created_at.strftime("%Y.%m.%d")

    def get_nickname(self, obj):
        return obj.user.nickname

    class Meta:
        model = ReviewModel
        exclude = ["updated_at", "goods"]
        extra_kwargs = {
            "user": {"required": False},
            "goods": {"required": False},
        }


class GoodsDetailSerializer(serializers.ModelSerializer):
    """
     Replace store with name
     Create a review set for the product
     """

    store_name = serializers.SerializerMethodField()
    store_user_id = serializers.SerializerMethodField()
    review_set = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    image_set = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    # fromat_price = serializers.SerializerMethodField()
    star_avg = serializers.SerializerMethodField()
    store_image = serializers.SerializerMethodField()
    store_id = serializers.SerializerMethodField()

    def get_store_name(self, obj):
        return obj.store.name

    def get_store_id(self, obj):
        return obj.store.id

    def get_review_set(self, obj):
        review = ReviewModel.objects.filter(goods_id=obj.id).order_by("-created_at")
        serializer = ReviewSerializer(review, many=True)
        return serializer.data

    def get_category(self, obj):
        return obj.category.name

    def get_image_set(self, obj):
        images = ImageModel.objects.filter(goods_id=obj.id)
        serializer = ImageSerializer(images, many=True)
        image_set = [i['image'] for i in serializer.data]
        return image_set

    def get_address(self, obj):
        address = obj.store.address
        # address = obj.store.address.split(' ')[:2]
        # address = ' '.join(address)
        return address

    def get_store_user_id(self, obj):
        return obj.store.seller.id

    def get_price(self, obj):
        return str(format_with_commas(obj.price)) + 'one'

    def get_store_image(self, obj):
        return obj.store.seller.profile_image.url if obj.store.seller.profile_image else False

    def get_star_avg(self, obj):
        review = ReviewModel.objects.filter(goods_id=obj.id).values("star")
        total = 0
        for i in review:
            total += i["star"]

        return math.ceil(total / review.count()) if total != 0 else 0

    # def get_format_price(self, obj):
    #     return str(format_with_commas(obj.price)) + '원'

    class Meta:
        model = GoodsModel
        exclude = ["created_at", "updated_at"]


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
        fields = "__all__"
        extra_kwargs = {
            "goods": {"required": False},
        }


class OrderSerializer(serializers.ModelSerializer):
    ordered_at = serializers.SerializerMethodField()
    goods_name = serializers.SerializerMethodField()
    store_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()

    def get_ordered_at(self, obj):
        return obj.ordered_at.strftime("%Y.%m.%d")

    def get_goods_name(self, obj):
        return obj.goods.name

    def get_store_name(self, obj):
        return obj.goods.store.name

    def get_user_name(self, obj):
        return obj.user.nickname

    class Meta:
        model = OrderModel
        fields = "__all__"

        extra_kwargs = {
            "user": {"required": False},
            "goods": {"required": False},
        }


class PostSerializer(serializers.Serializer):
    name = serializers.CharField(help_text="product name")
    price = serializers.IntegerField(help_text="product price")

    review = serializers.CharField(help_text="Review contents")

    search = serializers.CharField(help_text="What to search for")

    goods_id = serializers.IntegerField(help_text="Product ID to order")


class OnlyStoreGoodsSerializer(serializers.ModelSerializer):
    """
     Replace store with name
     Create a review set for the product
     """
    review_set = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    order_set = serializers.SerializerMethodField()
    goods_id = serializers.SerializerMethodField()
    image_set = serializers.SerializerMethodField()
    format_price = serializers.SerializerMethodField()
    star_avg = serializers.SerializerMethodField()

    def get_store(self, obj):
        return obj.store.name

    def get_review_set(self, obj):
        review = ReviewModel.objects.filter(goods_id=obj.id).order_by("-created_at")
        serializer = OnlyStoreReviewSerializer(review, many=True)
        return serializer.data

    def get_category(self, obj):
        return obj.category.name

    def get_order_set(self, obj):
        order = OrderModel.objects.filter(goods_id=obj.id).order_by("-ordered_at")
        serializer = OrderSerializer(order, many=True)
        return serializer.data

    def get_goods_id(self, obj):
        return obj.id

    def get_image_set(self, obj):
        images = ImageModel.objects.filter(goods_id=obj.id)
        serializer = ImageSerializer(images, many=True)
        image_set = [i['image'] for i in serializer.data]
        return image_set

    def get_format_price(self, obj):
        return str(format_with_commas(obj.price)) + 'one'

    def get_star_avg(self, obj):
        review = ReviewModel.objects.filter(goods_id=obj.id).values("star")
        total = 0
        for i in review:
            total += i["star"]

        return math.ceil(total / review.count()) if total != 0 else 0

    class Meta:
        model = GoodsModel
        fields = ["star_avg","goods_id", "review_set", "category", "order_set", "name", "price", "format_price", "description", "image_set"]


class OnlyStoreReviewSerializer(serializers.ModelSerializer):
    review_id = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    goods_id = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    user_profile = serializers.SerializerMethodField()

    def get_review_id(self, obj):
        return obj.id

    def get_user_name(self, obj):
        return obj.user.nickname

    def get_goods_id(self, obj):
        return obj.goods.id

    def get_created_at(self, obj):
        return obj.created_at.strftime("%Y.%m.%d")

    def get_user_profile(self, obj):
        return obj.user.profile_image.url if obj.user.profile_image else None

    class Meta:
        model = ReviewModel
        exclude = ["updated_at", "goods", "id"]
        extra_kwargs = {
            "user": {"required": False},
            "goods": {"required": False},
        }


class ChatStoreSerializer(serializers.Serializer):
    class Meta:
        model = StoreModel
        exclude = ["created_at", "updated_at"]


class GoodsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsModel
        exclude = ["store", "category"]
        extra_kwargs = {
            "description": {"required": False},
        }


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    cartitem_set = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = '__all__'

class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = '__all__'

class BillItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillItem
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'