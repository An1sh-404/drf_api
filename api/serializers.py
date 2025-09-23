from django.db import transaction
from rest_framework import serializers
from .models import Product, Order, OrderItem, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'is_staff',
            'is_superuser',
        )
        
        # fields = '__all__' # Not recommended



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        # speicify the model/table to be serialized
        model = Product

        # specify the fields to be serialized
        fields = (
            'id',
            'name',
            'description',
            'price',
            'stock',
        )

        read_only_fields = ['id']

    # validating if the value for the product is justifyable
    # syntax is validate_<nameofthefield>
    def validate_price(self,value):
        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than 0."
            )
        return value
    

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    product_price = serializers.DecimalField(
        max_digits = 10,
        decimal_places=2,
        source='product.price')

    # product = ProductSerializer()
    class Meta:
        model = OrderItem
        fields = ('product_name', 
                  'product_price',
                  'quantity', 
                  'item_subtotal'
                  )
        


class OrderCreateSerializer(serializers.ModelSerializer):
    class OrderItemCreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = OrderItem
            fields = ('product', 'quantity')

    order_id = serializers.UUIDField(read_only=True) 
    items = OrderItemCreateSerializer(many=True, required=False)

    def update(self, instance, validated_data):
        orderitem_data = validated_data.pop('items')
        
        with transaction.atomic():

            instance = super().update(instance, validated_data)

            if orderitem_data is not None:
                    # Clear exisiting items (optional, depends on requirements)
                instance.items.all().delete()
                    
                    # Recreate items with the updated data
                for item in orderitem_data:
                    OrderItem.objects.create(order=instance, **item)

        return instance


    def create(self, validated_data):
        orderitem_data = validated_data.pop('items')
        
        with transaction.atomic():

            order = Order.objects.create(**validated_data)

            for item in orderitem_data:
                OrderItem.objects.create(order=order,**item)

        return order

    class Meta:
        model = Order
        fields = (
            'order_id',
            'user',
            'status',
            'items',
        )
        extra_kwargs = {
            'user' : {'read_only' : True}
    
        } # can also use user = serializers.IntegerField(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(read_only=True)
    items = OrderItemSerializer(many=True,read_only=True) # if nested is not used then using just items in the field
    # would return the primary key only i.e commenting on items.
    
    total_price = serializers.SerializerMethodField() # serializer method usecase.

    def get_total_price(self,obj): # by default the method name is get_<methodfieldname> or directly specify the method name within the method field i.e
        # toatl_price = serializers.SerializerMethodField(method_name = 'total')
        order_items = obj.items.all()
        return sum(order_item.item_subtotal for order_item in order_items)


    class Meta:
        model = Order
        fields = ('order_id', 
                  'created_at',
                    'user',
                      'status',
                        'items',
                        'total_price',)


class ProductInfoSerializer(serializers.Serializer):
    # get all products, count of products, max price
    products = ProductSerializer(many=True)
    count = serializers.IntegerField()
    max_price  = serializers.FloatField()