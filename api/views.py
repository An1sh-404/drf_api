from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from api.serializers import ProductSerializer, OrderSerializer, OrderItemSerializer, ProductInfoSerializer, OrderCreateSerializer, UserSerializer
from api.models import Product, Order, OrderItem, User
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from rest_framework import generics
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    AllowAny,
)
from rest_framework.views import APIView
from api.filters import ProductFilter, OrderFilter, InstockFilterBackend
from rest_framework import filters,viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination,LimitOffsetPagination
from rest_framework.throttling import ScopedRateThrottle
from api.tasks import send_order_confirmation_email

# @api_view(['GET'])
# def product_list(request):
#     products = Product.objects.all() # gets all the product objects
#     serializer = ProductSerializer(products,many=True) # creates a serializer for the objects product. As its more than one so many true
#     # return JsonResponse({
#     #     'data' : serializer.data
#     #})
#     return Response(serializer.data)


# using generic classs based views

class ProductListCreateAPIView(generics.ListCreateAPIView):
    throttle_scope = 'products'
    throttle_classes = [ScopedRateThrottle]
    queryset = Product.objects.order_by('pk')
    #queryset = Product.objects.filter(stock__gt=0)
# filter out the product whose stock is greater than(gt) 0 i.e 
# only the product with stock value greater than zero are displayed.
    serializer_class = ProductSerializer
    # filterset_fields = ('name', 'price')
    filterset_class = ProductFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
        InstockFilterBackend, # ordering data in particular order
    ]

    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'stock']
    pagination_class = None # LimitOffsetPagination
    
    # pagination_class = PageNumberPagination
    # pagination_class.page_size = 2
    # pagination_class.page_query_param = 'pagenum'
    # pagination_class.page_size_query_param = 'size'
    # pagination_class.max_page_size = 6
    
    @method_decorator(cache_page(60 * 15, key_prefix='product_list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


    def get_queryset(self): 
        import time
        time.sleep(2)
        return super().get_queryset()

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == "POST":
            self.permission_classes = [IsAdminUser]
        
        return super().get_permissions()
    
    
    
    def get_serializer(self,*args,**kwargs):
        serializer = super().get_serializer(*args,**kwargs)

        if self.request.method == 'POST':
            serializer.fields.pop('id',None)
        
        return serializer
    # even though it also uses a post method here model is not defined it is due to that fact that when create() method is called from
    # CreateModelMixin it initializes a serializer i.e 
    # serializer = self.get_serializer(data=request.data) and then saves it after validation (serializer.is_valid())
    # this serializer.save() uses the model defined inside it to save the object to the database
    # and since ProductSerializer consists of model = Product 

# class ProductCreateAPIView(generics.CreateAPIView):
#     serializer_class = ProductSerializer 
    
#     def get_serializer(self,*args,**kwargs):
#         serializer = super().get_serializer(*args,**kwargs)

#         if self.request.method == 'POST':
#             serializer.fields.pop('id',None)
        
#         return serializer



# @api_view(['GET'])
# def product_detail(request,pk):
#     product = get_object_or_404(Product, pk=pk) # get a specific product with id as pk and creates an instance of Product class/table
#     serializer = ProductSerializer(product) # serializes a single object product
#     return Response(serializer.data)

# using generic class views

# class ProductDetailAPIView(generics.RetrieveAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     lookup_url_kwarg = 'product_id' # used to change the url keyword argument to product_id 
    # so that in url if urls : products/<int:product_id> is accessed it access the data through specific field.

# new


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_url_kwarg = 'product_id'

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ['PUT','PATCH','DELETE']:
            self.permission_classes = [IsAdminUser]

        return super().get_permissions()


# @api_view(['GET'])
# def order_list(request):
#     #orders = Order.objects.all() # gets all the order objects
#     #    Query 1: Fetch all Order objects.

#     #    Query 2: Fetch all OrderItem objects where order_id is in the orders.

#     #     Query 3: Fetch all Product objects related to those OrderItems.
    
#     orders = Order.objects.prefetch_related(#'items',
#                                             'items__product',
#                                             ).all()
#     print(orders)
#     serializer = OrderSerializer(orders,many=True) # creates a serializer for the objects order. As its more than one so many true

#     return Response(serializer.data)


# class OrderListAPIView(generics.ListAPIView):
#     queryset = Order.objects.prefetch_related('items__product')
#     serializer_class = OrderSerializer

# class UserOrderListAPIView(generics.ListAPIView):
#     queryset = Order.objects.prefetch_related('items__product')
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         qs = super().get_queryset() # generics.ListAPIView already has a get_queryset() 
        # method that returns self.queryset. This means for each request UserOrderListAPIView
        # class instance is created and queryset is set and then the method defined i.e get_queryset(self) is
        # also called and since qs = super().get_queryset() --> super() allows user to access methods
        # defined in parent class (generics.ListAPIView) here method returns self.queryset and
        # finally this queryset is filtered so that it returns orders of the requested user only.
        # return qs.filter(user = self.request.user)


class OrderViewSet(viewsets.ModelViewSet): # CRUD operations exists in ModelViewset
    throttle_scope = 'orders'
    throttle_classes = [ScopedRateThrottle]
    
    # items - fetches all OrderItem objects related to each Order
    # __product - for each OrderItem, also fetch the associated Product object
    queryset = Order.objects.prefetch_related('items__product')
    
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend]

    @method_decorator(cache_page(60 * 15, key_prefix='order_list'))
    @method_decorator(vary_on_headers("Authorization"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)



    # To pass additional parameters/arguments to a a serializer.save() method
    
    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        send_order_confirmation_email.delay(order.order_id, self.request.user.email)

    def get_serializer_class(self):
        # can also check if POST: if self.request.method == 'POST'
        if self.action == 'create' or self.action == 'update':
            return OrderCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs
    

    # @action(
    #         detail=False, methods=['get'], 
    #         url_path='user-orders',
    #         # permission_classes=[IsAuthenticated],
    #         )
    # def user_orders(self,request):
    #     orders = self.get_queryset().filter(user=request.user)
    #     serializer = self.get_serializer(orders,many=True)
    #     return Response(serializer.data)



class ProductInfoAPIView(APIView):
    def get(self,request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer({
            'products' : products,
            'count' : len(products),
            'max_price' : products.aggregate(max_price=Max('price'))['max_price'] # to calculate the maximum 
            # price of the product from the price field n  Product model. products.aggregate returns a dictionary
            # with 'max_price' : value so we add max_price at the end to get only the value.
        })
        return Response(serializer.data)



# @api_view(['GET'])
# def product_info(request):
#     products = Product.objects.all()
#     serializer = ProductInfoSerializer({
#         'products' : products,
#         'count' : len(products),
#         'max_price' : products.aggregate(max_price = Max('price'))['max_price'],
#     })
#     return Response(serializer.data)

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = None

