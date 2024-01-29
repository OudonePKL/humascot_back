import base64
import uuid
from collections import Counter
from pprint import pprint
from PIL import Image
import io
import django
from django.core.files.base import ContentFile
from django.db.models import Q, Count
from django.shortcuts import render, redirect
from rest_framework import status, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics

from chat.views import get_user_id_from_token
from .form import ReviewForm
from .models import (
    GoodsModel,
    StoreModel,
    ReviewModel,
    BookmarkModel,
    OrderModel,
    FilteringModel, ImageModel, CategoryModel, PolicyModel,
    Cart, CartItem,
    Bill, BillItem, Payment
)
from .serializers import (
    StoreSerializer,
    GoodsSerializer,
    ReviewSerializer,
    GoodsDetailSerializer,
    OrderSerializer,
    PostSerializer,
    UpdateStoreSerializer,
    ImageSerializer,
    GoodsCreateSerializer,
    CartSerializer, CartItemSerializer,
    BillSerializer, BillItemSerializer, PaymentSerializer
)

from drf_yasg.utils import swagger_auto_schema

"""
Permission to divide general users, merchants, and administrators
"""


class IsSeller(BasePermission):
    def has_permission(self, request, view):
        try:
            seller = request.user.is_seller
            admin = request.user.is_admin
            if seller or admin:
                return True
            else:
                return False
        except:
            # If login
            return False


class GoodsView(APIView):
    @swagger_auto_schema(tags=["View product list and details"], responses={200: "Success"})
    def get(self, request, goods_id=None):
        """
         <View product>
         goods_id O -> View details
         goods_id
         * Separately removed due to merchant permission issues *
         """
        if goods_id is None:
            category = request.GET.get('category', '1')  # You can provide default values.
            goods = GoodsModel.objects.all()
            if not goods.exists():
                return Response([], status=200)
            """
             <Filtering branch>
             - Latest
             - Old shoots
             - Price ascending & descending order
             - Ascending & descending number of reviews (5,6)
             """
            if category == '2':
                goods = goods.order_by(
                    "-price"
                )
            elif category == '3':
                goods = goods.annotate(review_count=Count("reviewmodel")).order_by(
                    "-review_count"
                )
            elif category == '4':
                goods = goods.order_by(
                    "price"
                )
            elif category == '5':
                goods = goods.annotate(order_count=Count("ordermodel")).order_by(
                    "-order_count"
                )
            elif category == '6':
                goods = goods.annotate(order_count=Count("ordermodel")).order_by(
                    "-created_at"
                )
            else:
                try:
                    goods = goods.order_by("-price")
                except Exception as e:
                    print(e)
                    return Response(
                        {"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
                    )
            serializer = GoodsSerializer(goods, many=True)
            return Response(serializer.data, status=200)
        else:
            goods = get_object_or_404(GoodsModel, id=goods_id)
            serializer = GoodsDetailSerializer(goods)
            order_total = OrderModel.objects.filter(user_id=request.user.id, goods=goods).count()
            review_total = ReviewModel.objects.filter(user_id=request.user.id, goods=goods).count()
            result = serializer.data.copy()
            if order_total >= review_total:
                result['is_ordered'] = True
            else:
                result['is_ordered'] = False
            return Response(result, status=200)


class StoreView(APIView):
    # permission_classes = [IsSeller]

    @swagger_auto_schema(tags=["Store information & product registration & store modification"], responses={200: "Success"})
    def get(self, request, store_id):
        """
         <View store information>
         - Store basic information
         - List of products in the store
         """
        store = get_object_or_404(StoreModel, id=store_id)
        serializer = StoreSerializer(store)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Store information & product registration & store modification"],
        request_body=PostSerializer,
        responses={200: "Success"},
    )
    def post(self, request, store_id):
        """
         <Product registration>
         Will be converted to multiple images
         """
        if request.data.get('goods_set'):
            for data in request.data.get("goods_set"):
                if data:
                    serializer = GoodsCreateSerializer(data=data)
                    category, is_created = CategoryModel.objects.get_or_create(name=data.get('category'))
                    if serializer.is_valid():
                        instance = serializer.save(category=category, store_id=store_id)
                        images_data = data.get('images', [])
                        if images_data:
                            for image_data in images_data:
                                format, imgstr = image_data.split(';base64,')
                                ext = format.split('/')[-1]
                                file_data = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')
                                ImageModel.objects.create(goods=instance, image=file_data)
            return Response({"message": "The product has been registered."}, status=status.HTTP_201_CREATED)
        return Response({"message": "A problem has occurred."}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["Store information & product registration & store modification"],
        request_body=PostSerializer,
        responses={200: "Success"},
    )
    def patch(self, request, store_id=None):
        store = get_object_or_404(StoreModel, id=store_id)
        data = {}
        try:
            for k, v in request.data.items():
                if v:
                    data[k] = v
        except Exception as e:
            return Response(
                {"message": 'A problem has occurred.'}, status=status.HTTP_400_BAD_REQUEST
            )
        if request.data.get("store_name"):
            return Response(
                {"message": "The store name cannot be changed."}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UpdateStoreSerializer(store, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Store information has been modified."}, status=status.HTTP_200_OK)
        return Response(
            {"message": str(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST
        )

class StoreCreateAPIView(generics.CreateAPIView):
    queryset = StoreModel.objects.all()
    serializer_class = StoreSerializer

class GoodsPatchView(APIView):
    permission_classes = [IsSeller]

    @swagger_auto_schema(
        tags=["Multiple product modifications"],
        request_body=PostSerializer,
        responses={200: "Success"},
    )
    def patch(self, request):
        if request.data.get('goods_set'):
            for data in request.data.get("goods_set"):
                if data:
                    data = data.copy()
                    if 'one' in data['price']:
                        data['price'] = data['price'][:-1]
                    goods = get_object_or_404(GoodsModel, id=data.get("id"))
                    serializer = GoodsSerializer(goods, data=data, partial=True)
                    category, is_created = CategoryModel.objects.get_or_create(name=data.get('category'))
                    if serializer.is_valid():
                        instance = serializer.save(category=category)
                        images_data = data.get('images', [])
                        if images_data:
                            instance.imagemodel_set.all().delete()
                            for idx, image_data in enumerate(images_data):
                                # Convert Base64 encoded string to image file
                                # Delete all existing images and save as new -> It would be better to select the image and edit it later.
                                format, imgstr = image_data.split(';base64,')
                                ext = format.split('/')[-1]
                                file_data = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')
                                # Create a new image object and save it with the image file
                                ImageModel.objects.create(goods=instance, image=file_data)
                    else:
                        print(serializer.errors)
            return Response({"message": "The product has been modified."}, status=status.HTTP_200_OK)
        return Response({"message": "A problem has occurred."}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        if request.data.get('goods_id'):
            goods = get_object_or_404(GoodsModel, id=request.data.get("goods_id"))
            goods.delete()
        return Response({"message": "success"}, status=status.HTTP_200_OK)


class ReviewView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    """
     <Logic related to reviews>
     Edit and delete review -> pk = id of review
     """

    @swagger_auto_schema(tags=["View and write product reviews"], responses={200: "Success"})
    def get(self, request, pk):
        # pk = product id
        review = ReviewModel.objects.filter(goods_id=pk).order_by("-created_at")
        serializer = ReviewSerializer(review, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["View and write product reviews"], request_body=PostSerializer, responses={201: "Created"}
    )
    def post(self, request, pk):
        # pk = product id
        review = ReviewModel.objects.filter(user=request.user, goods_id=pk).exists()
        order = OrderModel.objects.filter(user=request.user, goods_id=pk).exists()
        if not order:
            return Response({"message": "Only users who have placed an order can leave a review."}, status=status.HTTP_400_BAD_REQUEST)
        if review:
            return Response({"message": "I've already written a review."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(goods_id=pk, user=request.user)
            return Response({"message": "Review completed"}, status=status.HTTP_201_CREATED)
        return Response({"message": "Please use after logging in."}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        review = get_object_or_404(ReviewModel, id=pk, user=request.user)
        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "success"}, status=status.HTTP_200_OK)
        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        review = get_object_or_404(ReviewModel, id=pk, user=request.user)
        review.delete()
        return Response({"message": "success"}, status=status.HTTP_200_OK)


class CheckReview(APIView):
    def post(self, request, pk):
        review = ReviewModel.objects.filter(user=request.user, goods_id=pk).exists()
        order = OrderModel.objects.filter(user=request.user, goods_id=pk).exists()
        if not order:
            return Response({"message": "Only users who have placed an order can leave a review."}, status=status.HTTP_400_BAD_REQUEST)
        if review:
            return Response({"message": "I've already written a review."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "success"}, status=status.HTTP_200_OK)


class TermsAPI(APIView):
    def get(self, request, pk):
        # 1: Terms of Use, 2: Privacy Policy
        turm = PolicyModel.objects.filter(category=pk).last()
        content = turm.content if turm else ""
        return Response({"content": content}, status=status.HTTP_200_OK)


class OrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    """
     <Product order logic>
     """

    @swagger_auto_schema(tags=["Product ordering and inquiry"], responses={200: "Success"})
    def get(self, request):
        order_set = (
            OrderModel.objects.filter(user=request.user).distinct().values("goods")
        )
        data = []
        if order_set:
            for order in order_set:
                goods = GoodsModel.objects.get(id=order['goods'])
                data.append(GoodsSerializer(goods).data)
            return Response(data, status=status.HTTP_200_OK)
        return Response([], status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=["Product ordering and inquiry"], request_body=PostSerializer, responses={200: "Success"}
    )
    def post(self, request):
        goods_id = request.data.get("goods_id")

        goods = get_object_or_404(GoodsModel, id=goods_id)
        goods = GoodsSerializer(goods).data.copy()

        serializer = OrderSerializer(data=goods)

        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save(user=request.user, goods_id=goods_id)
                return Response({"message": "I ordered a product."}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SearchView(APIView):
    @swagger_auto_schema(
        tags=["search"], request_body=PostSerializer, responses={200: "Success"}
    )
    def post(self, request):
        search_word = request.data.get("search")
        goods_set = GoodsModel.objects.filter(
            Q(name__icontains=search_word) | Q(store__name__icontains=search_word)
        )

        goods = GoodsSerializer(goods_set, many=True).data

        return Response(goods, status=status.HTTP_200_OK)


def resize_image(image_data, output_size=(800, 600), quality=85):
    """
     Adjust the resolution of the image file and save it in JPEG format.
     :param image_data: Original image data (base64 encoded string).
     :param output_size: Size (width, height) of the image to be changed.
     :param quality: JPEG storage quality (1-100).
     :return: Changed image data (base64 encoded string).
     """
    # Convert image data to PIL image object
    image = Image.open(io.BytesIO(base64.b64decode(image_data)))

    # Change image size
    image = image.resize(output_size, Image.ANTIALIAS)

    # Save in JPEG format
    output_buffer = io.BytesIO()
    image.save(output_buffer, format='JPEG', quality=quality)
    output_data = base64.b64encode(output_buffer.getvalue()).decode()

    return output_data



# ============================= For user =============================
# Cart management
class CartListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsSeller]

    queryset = Cart.objects.all()
    serializer_class = CartSerializer

class CartDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsSeller]

    queryset = Cart.objects.all()
    serializer_class = CartSerializer

class CartItemListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsSeller]

    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsSeller]

    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer


# Bill and Payment management
class BillListCreateView(generics.ListCreateAPIView):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer

class BillDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer

class BillItemCreateView(generics.CreateAPIView):
    queryset = BillItem.objects.all()
    serializer_class = BillItemSerializer

class PaymentListCreateView(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class PaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


