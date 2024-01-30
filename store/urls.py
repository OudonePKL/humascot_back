from django.conf.urls.static import static
from django.urls import path
from django.conf import settings
from store import views


urlpatterns = [
    path("", views.GoodsView.as_view(), name="goods_list"),  # Product list related
    path('categories', views.CategoryListCreateAPIView.as_view(), name='categories-list'),
    path("detail/<int:goods_id>", views.GoodsView.as_view(), name="goods_detail"),  # Product list related
    path("<int:store_id>", views.StoreView.as_view(), name="store"),  # Store Related Related
    path("store-signup", views.StoreCreateAPIView.as_view(), name="store-signup"),  
    path(
        "goods", views.GoodsPatchView.as_view(), name="goods_change"
    ),  # Related to modifying goods -> Different view placement due to permission settings
    path(
        "goods/<int:goods_id>", views.GoodsView.as_view(), name="goods_detail"
    ),  # Product related
    path("review/<int:pk>", views.ReviewView.as_view(), name="review"),  # Review related
    path("order", views.OrderView.as_view(), name="order"),  # Order related
    path("search", views.SearchView.as_view(), name="search"),  # Order related
    path("check-review/<int:pk>", views.CheckReview.as_view(), name="CheckReview"),  # Order related
    path("terms/<int:pk>", views.TermsAPI.as_view(), name="terms"),  # Order related
    # Cart
    path('carts', views.CartListCreateView.as_view(), name='cart-list-create'),
    path('carts/<int:pk>', views.CartDetailView.as_view(), name='cart-detail'),
    path('carts/user/<int:user_id>/', views.CartByUserAPIView.as_view(), name='cart-by-user'),
    path('cart-items', views.CartItemListCreateView.as_view(), name='cartitem-list-create'),
    path('cart-items/<int:pk>', views.CartItemDetailView.as_view(), name='cartitem-detail'),
    # Bill and Payment
    path('bills', views.BillListCreateView.as_view(), name='bill-list-create'),
    path('bills/<int:pk>', views.BillDetailView.as_view(), name='bill-detail'),
    path('bills/user/<int:user_id>/', views.BillByUserAPIView.as_view(), name='bill-by-user'),
    path('bill-items', views.BillItemCreateView.as_view(), name='billitem-create'),
    path('payments', views.PaymentListCreateView.as_view(), name='payment-list-create'),
    path('payments/<int:pk>', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('payments/user/<int:user_id>/', views.PaymentByUserAPIView.as_view(), name='payment-by-user'),
]
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
