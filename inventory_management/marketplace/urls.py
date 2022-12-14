from django.urls import path
from marketplace.views import (
    CreateProductAPIView,
    EditProductAPIview,
    DeleteProductAPIView,
    ProductAPIListView,
    ProductDetailAPIView,
    CreateOrderAPIView,
    PurchaseOrderAPIView,
    CancelOrderAPIView
)

urlpatterns = [
    path('products/', ProductAPIListView.as_view(), name='list_products'),
    path('products/<str:category>/', ProductAPIListView.as_view(), name='products_by_categories'),
    path('product/add/', CreateProductAPIView.as_view(), name='create_product'),
    path('product/<str:prod_id>/', ProductDetailAPIView.as_view(), name='view_product_detail'),
    path('product/<str:prod_id>/edit/', EditProductAPIview.as_view(), name='edit_product'),
    path('product/<str:prod_id>/delete/', DeleteProductAPIView.as_view(), name='delete_product'),
    path('order/add/', CreateOrderAPIView.as_view(), name="create_order"),
    path('order/<str:order_id>/buy/', PurchaseOrderAPIView.as_view(), name='purchase_order'),
    path('order/<str:order_id>/cancel/', CancelOrderAPIView.as_view(), name='cancel_order'),
]