from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, exceptions
from rest_framework.response import Response
from .models import Category, MenuItem, Cart, Order, OrderItem, CartItem
from .serializers import MenuItemSerializer, OrderSerializer, CartSerializer, CategorySerializer, AddToCartSerializer, GroupsSerializer
from django.contrib.auth.models import User, Group
from djoser.serializers import ActivationSerializer
from rest_framework.decorators import api_view, permission_classes, authentication_classes, throttle_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.shortcuts import get_object_or_404
from rest_framework import status
from djoser.serializers import UserSerializer
from django.core.paginator import Paginator, EmptyPage
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

@throttle_classes([AnonRateThrottle, UserRateThrottle])
class MenuItemsViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price']
    filterset_fields = ['price']
    search_fields = ['title']

    def get_permissions(self):
        if(self.request.method=='GET') | self.request.user.groups.filter(name='Manager').exists():
            return []
        raise exceptions.PermissionDenied

class OrdersViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    ordering_fields = ['date']
    filterset_fields = ['total']
    search_fields = ['date']

    def list(self, request):
        search = request.query_params.get('search')
        to_price = request.query_params.get('to_price')
        perpage = request.query_params.get('perpage', default=2)
        page = request.query_params.get('page', default=1)
        items = []
        if not request.user.is_authenticated:
            return Response({"error": "You must be logged in to see the orders."}, status=401)
        if not request.user.groups.filter(name='Manager').exists():
            if request.user.groups.filter(name="Delivery crew").exists():
                items = Order.objects.filter(delivery_crew=request.user)
            else:
                items = Order.objects.filter(user=request.user)
        else:
            items = Order.objects.all()

        # search
        if to_price:
            items = items.filter(total=to_price)
        if search:
            items = items.filter(date__contains=search)
        # pagination
        paginator = Paginator(items, per_page=perpage)
        try:
            items = paginator.page(number=page)
        except EmptyPage:
            items = []
        serializer = OrderSerializer(items, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk):
        if not request.user.is_authenticated:
            return Response({"error": "You must be logged in to see the orders."}, status=401)
        if not request.user.groups.filter(name='Manager').exists():
            if request.user.groups.filter(name="Delivery crew").exists():
                try:
                    queryset = Order.objects.get(pk=pk, delivery_crew=request.user)
                except Order.DoesNotExist:
                    return Response({"error": "Order is not found"}, status=400)
            else:
                try:
                    queryset = Order.objects.get(pk=pk, user=request.user)
                except Order.DoesNotExist:
                    return Response({"error": "Order is not found"}, status=400)
                
            serializer = self.get_serializer(queryset)
            return Response(serializer.data)
        else:
            try:
                queryset = Order.objects.get(pk=pk)
            except Order.DoesNotExist:
                return Response({"error": "Order is not found"}, status=400)
            serializer = self.get_serializer(queryset)
            return Response(serializer.data)
        
    def create(self, request):
        # Get the user's cart
        cart = []
        try:
            cart = Cart.objects.filter(user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Your cart is empty."}, status=400)

        print(cart.all())
        if len(cart.all())<1:
            return Response({"error": "Your cart is empty."}, status=400)

        # Create the order
        order = Order.objects.create(user=request.user)

        # Create order items
        for cart_item in cart.all():
            item_total = cart_item.price
            item = OrderItem.objects.create(
                order=order,
                menuitem=cart_item.menuitem,
                quantity=cart_item.quantity,
                unit_price=cart_item.menuitem.price,
                price=item_total,
            )
            item.save()
            print("item_total:",item_total,"total:",order.total)
            order.total += item_total

        print("order total: ", order.total)
        order.save()
        # Clear the cart
        cart.delete()
        return Response({"message": "Order created successfully."})

    def update(self, request, pk):
        if not request.user.is_authenticated:
            return Response({"error": "You must be logged in to update the order."}, status=401)
        if not request.user.groups.filter(name='Manager').exists():
            try:
                queryset = Order.objects.get(pk=pk, delivery_crew=request.user)
            except Order.DoesNotExist:
                return Response({"error": "Order is not found or don't have the permission"}, status=400)
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            queryset.status = serializer.validated_data['status']
            queryset.save()
            return Response({"message":"updated status"})
        else:
            try:
                queryset = Order.objects.get(pk=pk)
            except Order.DoesNotExist:
                return Response({"error": "Order is not found"}, status=400)
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            if serializer.validated_data['status']:
                queryset.status = serializer.validated_data['status']
            #if serializer.validated_data['delivery_crew_id']:
            #    queryset.delivery_crew = serializer.validated_data['delivery_crew_id']
            crewuser = request.data['delivery_crew']
            if crewuser:
                crewuser = get_object_or_404(User, id=crewuser)
                queryset.delivery_crew = crewuser
            queryset.save()
            return Response({"message":"updated status"})
        
    def get_permissions(self):
        if(self.request.method=='DELETE'):
            if self.request.user.groups.filter(name='Manager').exists():
                return []
            else:
                raise exceptions.PermissionDenied
        return []

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    #create = serializers.SerializerMethodField(method_name="add_to_cart")

    def list(self, request):
        queryset = Cart.objects.filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        menu_id = serializer.validated_data['menu_id']
        quantity = serializer.validated_data['quantity']

        # Check if user is authenticated
        if not request.user.is_authenticated:
            return Response({"error": "You must be logged in to add to cart."}, status=401)

        
        # Check if the menu item exists
        try:
            menuitem = MenuItem.objects.get(pk=menu_id)
        except MenuItem.DoesNotExist:
            return Response({"error": "Menu item not found."}, status=404)

        # Get or create a cart for the user
        cart, created = Cart.objects.get_or_create(user=request.user, quantity=quantity, menuitem=menuitem,unit_price=menuitem.price, price=quantity*menuitem.price)
        
        # Create or update cart item
        cart_item, created = CartItem.objects.get_or_create(cart=cart, menuitem=menuitem, quantity=quantity)
        cart_item.save()

        # Update cart total price
        #cart.update_total_price()
        print("saving the cart...")
        cart.save()

        return Response({"message": "Item added to cart."})

    def destroy(self, request):
        queryset = Cart.objects.filter(user=request.user)
        queryset.delete()
        return Response({"message":"deleted all cart items"})

    

class GroupsViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupsSerializer
    def get_permissions(self):
        if not self.request.user.groups.filter(name='Admin').exists():
            raise exceptions.PermissionDenied


class GroupUsersViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupsSerializer
    def list(self, request):
        queryset = Group.objects.filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class GroupUserDeleteViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupsSerializer
    def list(self, request):
        queryset = Group.objects.filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# groups
@api_view(['GET', 'POST', 'DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def groups(request, groupname):
    if not request.user.groups.filter(name='Manager').exists():
        raise exceptions.PermissionDenied
    # conver the group name first letter to capital letter
    camel_group_name = groupname[0].upper()+groupname[1:]
    if request.method == 'GET':
        users = User.objects.filter(groups__name=camel_group_name)
        serializer = UserSerializer(users, many=True)
        return Response({'data': serializer.data})
    username = request.data['username']
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(groups__name=camel_group_name)
        if request.method == 'POST':
            managers.user_set.add(user)
        elif request.method == 'DELETE':
            managers.user_set.remove(user)
        return Response({"message": 'ok'})

    return Response({'message': 'error'}, status.HTTP_400_BAD_REQUEST)