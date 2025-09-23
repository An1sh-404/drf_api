from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
urlpatterns = [
    path('products/',views.ProductListCreateAPIView.as_view(),name='product_list_create'),
    # path('products/create/',views.ProductCreateAPIView.as_view(),name='product_create'),
    path('products/info/',views.ProductInfoAPIView.as_view(),name='product_info'),
    path('products/<int:product_id>/',views.ProductDetailAPIView.as_view(),name='product_detail'),
    # path('orders/',views.OrderListAPIView.as_view(),name='order_list'),
    # path('user-orders/',views.UserOrderListAPIView.as_view(),name='user_order'),
    path('users/',views.UserListView.as_view()),

]

router = DefaultRouter()
router.register('orders',views.OrderViewSet)
urlpatterns += router.urls