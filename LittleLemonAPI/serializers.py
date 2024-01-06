from rest_framework import serializers 
from .models import MenuItem, Cart, Order, OrderItem, Category, CartItem 
from rest_framework.validators import UniqueTogetherValidator 
from django.contrib.auth.models import User, Group
from djoser.serializers import ActivationSerializer
 

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['title']
        queryset = Category.objects.all()

 
class MenuItemSerializer (serializers.ModelSerializer): 
    class Meta:
        model = MenuItem
        fields = ['id','title', 'price', 'featured', 'category']
        
class OrderItemSerializer (serializers.ModelSerializer):
    menuitem = serializers.StringRelatedField(read_only=True)
     
    class Meta:
        model = OrderItem
        fields = ['id','menuitem', 'unit_price', 'quantity', 'price', 'order_id']

class OrderSerializer (serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField( 
    queryset=User.objects.all(), 
    default=serializers.CurrentUserDefault() 
    )
    class Meta:
        model = Order
        fields = ['id','user', 'delivery_crew', 'status', 'total','date']
        queryset = Order.objects.all()
    
    def to_representation(self, instance):
            data = super().to_representation(instance)
            orderitems = OrderItem.objects.filter(order=instance)
            items = OrderItemSerializer(orderitems, many=True, context=self.context)
            data['items'] = items.data
            return data

class CartSerializer (serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField( 
    queryset=User.objects.all(), 
    default=serializers.CurrentUserDefault() 
    )
    class Meta:
        model = Cart
        fields = ['id', 'user', 'menuitem', 'quantity', 'unit_price','price']
        queryset = Cart.objects.all()
        extra_kwargs = {
            'user': {'read_only': True},
        }
    
    def to_representation(self, instance):
            # Only show carts belonging to the current user
            if self.context['request'].user != instance.user:
                raise serializers.ValidationError('You can only access your own cart.')
            data = super().to_representation(instance)
            cartitems = CartItem.objects.filter(cart=instance)
            items = CartItemSerializer(cartitems, many=True, context=self.context)
            data['items'] = items.data
            return data


class CartItemSerializer(serializers.ModelSerializer):
    menuitem = serializers.StringRelatedField(read_only=True)
    price = serializers.SerializerMethodField()
    unit_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'menuitem','quantity','unit_price', 'price']

    def get_price(self, cart_item):
        return cart_item.menuitem.price * cart_item.quantity
    
    def get_unit_price(self, cart_item):
        return cart_item.menuitem.price


class AddToCartSerializer(serializers.Serializer):
    menu_id = serializers.IntegerField()
    quantity = serializers.IntegerField()



#---

class GroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        queryset = Group.objects.all()
        fields = '__all__'