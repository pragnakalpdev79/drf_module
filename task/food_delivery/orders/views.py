import logging
from django.db.models import Sum,F
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status,viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .throttles import *
from user.models import *
from user.permissions import IsRestaurantOwner,IsCustomer,IsDriver
from .serializers import *
from .pagination import OrdersPagination,ReviewPagination

logger = logging.getLogger('user')

#===============================================================================================
# 1. CART VIEWSET - add or remove or view cart items
class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsCustomer]
    throttle_classes = [OrderCreateT]
    throttle_scope = 'checkout'

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user).select_related('menu_item')

    def perform_create(self,serializer):
        serializer.save(user=self.request.user)
        logger.info(f"===item added to cart by {self.request.user.email}===")
    #==================================================================================
    # 1.1 add to cart - if item already exists just update quantity
    @action(detail=False,methods=['post'])
    def addtocart(self,request):
        logger.info("1.ADD TO CART VIEW")
        menu_item_id = request.data.get('menu_item')
        quantity = int(request.data.get('quantity',1))
        logger.info(f"1.1===adding item {menu_item_id} to cart===")

        try:
            menu_item = MenuItem.objects.get(id=menu_item_id)
        except MenuItem.DoesNotExist:
            return Response({'error':'menu item not found'},status=status.HTTP_404_NOT_FOUND)

        if not menu_item.is_available:
            return Response({'error':f'{menu_item.name} is not available right now'},status=status.HTTP_400_BAD_REQUEST)

        #check if already in cart
        existing = CartItem.objects.filter(user=request.user,menu_item=menu_item).first()
        if existing:
            existing.quantity += quantity
            existing.save(update_fields=['quantity'])
            logger.info(f"1.2 ===updated quantity to {existing.quantity}===")
            serializer = CartItemSerializer(existing)
        else:
            cart_item = CartItem.objects.create(user=request.user,menu_item=menu_item,quantity=quantity)
            serializer = CartItemSerializer(cart_item)
            logger.info(f"1.2 Menu-Item added to the cart")

        return Response({
            'message': 'item added to cart',
            'item': serializer.data,
        })
    #==================================================================================
    # 1.2 view full cart with total
    @action(detail=False,methods=['get'])
    def mycart(self,request):
        items = self.get_queryset()
        serializer = CartItemSerializer(items,many=True)
        cart_total = sum(item.menu_item.price * item.quantity for item in items)
        return Response({
            'items': serializer.data,
            'cart_total': cart_total,
            'item_count': items.count(),
        })
    #==================================================================================
    # 1.3 clear the ENTIRE CART
    @action(detail=False,methods=['delete'])
    def clear(self,request):
        logger.info("---------Cart empty request-----------")
        count = CartItem.objects.filter(user=request.user).delete()[0]
        logger.info(f"===cart cleared, {count} items removed===")
        return Response({'message':f'cart cleared, {count} items removed'})
    
    #==================================================================================
    # 1.4 CHECKOUT - CONVERT CART TO ORDER MOCK PAYMENT
    @action(detail=False,methods=['post'],throttle_classes=[OrderCreateT])
    def checkout(self,request):
        logger.info(f"===checkout started for {request.user.email}===")
        cart_items = CartItem.objects.filter(user=request.user).select_related('menu_item','menu_item__restaurant')

        if not cart_items.exists():
            return Response({'error':'cart is empty'},status=status.HTTP_400_BAD_REQUEST)

        #check all items from same restaurant
        restaurants = set(item.menu_item.restaurant_id for item in cart_items)
        if len(restaurants) > 1:
            return Response({'error':'all items must be from same restaurant'},status=status.HTTP_400_BAD_REQUEST)

        restaurant = cart_items.first().menu_item.restaurant
        #checking minimum order of resto
        cart_total = sum(item.menu_item.price * item.quantity for item in cart_items)
        if cart_total < restaurant.minimum_order:
            return Response({
                'error':f'minimum order is Rs.{restaurant.minimum_order}, your cart is Rs.{cart_total}'
            },status=status.HTTP_400_BAD_REQUEST)

        #get delivery address
        try:
            dadr = request.user.customer_profile.default_adress
            tadr = dadr.address
        except Exception:
            return Response({'error':'please set a default address first'},status=status.HTTP_400_BAD_REQUEST)

        special = request.data.get('special_instructions','')
        confirm = request.data.get('confirm',False)

        if not confirm:
            return Response({
                'message': 'review your order and send confirm=true to place',
                'restaurant': restaurant.name,
                'items': CartItemSerializer(cart_items,many=True).data,
                'cart_total': cart_total,
                'delivery_fee': restaurant.delivery_fee,
                'delivery_address': dadr.address,
            })

        #confirmed - create the order
        logger.info("===order confirmed, creating===")
        order = Order.objects.create(
            customer=request.user,
            restaurant=restaurant,
            delivery_address=dadr,
            special_instructions=special,
            adratorder=tadr,
        )

        #converting cart items to order items
        for ci in cart_items:
            OrderItem.objects.create(
                order=order,
                menu_item=ci.menu_item,
                quantity=ci.quantity,
                uprice=ci.menu_item.price,
            )
            logger.info(f"item: {ci.menu_item.name} * {ci.quantity} at the price {ci.menu_item.price}")

        #calculate total
        order.calculate_total()

        #clear cart
        cart_items.delete()
        logger.info(f"===order {order.order_number} placed, cart cleared===")

        return Response({
            'message': 'order placed successfully!',
            'order': OrderSerializer(order).data,
        },status=status.HTTP_201_CREATED)

#===============================================================================================
# ORDER VIEWSET - view/manage orders
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.select_related('customer','restaurant','driver').prefetch_related('item_for__menu_item')
        #THIS VIEW WILL BE USED BY ALL 3  
        if user.check_if_customer: 
            return qs.filter(customer=user)
        elif user.check_if_driver:
            return qs.filter(driver=user)
        elif user.check_if_restaurant:
            return qs.filter(restaurant__owner=user)
        return qs

    #===============================================================================================
    # STATUS UPDATE
    @action(detail=True,methods=['patch'])
    def update_status(self,request,pk=None):
        order = self.get_object(order_number=pk)
        logger.info(f"===status update for order {order.order_number}===")
        serializer = OrderStatusUpdateSerializer(
            data=request.data,
            context={'order':order,'request':request}
        )
        logger.info(" 1.1 **********************************************8")
        logger.info("validating with serializer")
        serializer.is_valid(raise_exception=True)
        logger.info("1.2 **********************************************8")
        logger.info("validated with serializer")
        new_status = serializer.validated_data['status']
        logger.info("1.3 **********************************************8")
        logger.info("validating with serializer updated status in validated data")
        try:
            order._transition(new_status)
            logger.info("worked")
            return Response(OrderSerializer(order).data)
        except Exception as e:
            logger.info("did not work")
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True,methods=['post'])
    def assign_driver(self,request,pk=None):
        order = self.get_object()
        print(order) #order id will be passed from post request url
        logger.info(f"+++++++++++++++++++++++++++++++++++++++++++++")
        logger.info(f"Assign driver request for or    der -- {order}")
        driver_id = request.data.get('driver_id')
        logger.info(f"===assigning driver {driver_id}===")
        try:
            driver = CustomUser.objects.get(id=driver_id,utype='d')
            #dp = driver.driver_profile
            dp = DriverProfile.objects.get(user_id=driver_id)
            print(driver)
            print(dp)
            print(dp.is_available)
            if not dp.is_available:
                return Response({'error':'driver is busy'},status=status.HTTP_400_BAD_REQUEST)
            order.driver = driver
            order.save(update_fields=['driver'])
            dp.is_available = False
            dp.save(update_fields=['is_available'])
            return Response({'message':f'driver {driver.first_name} assigned'})
        except CustomUser.DoesNotExist:
            return Response({'error':'driver not found'},status=status.HTTP_404_NOT_FOUND)

    @action(detail=True,methods=['post'])
    def cancel(self,request,pk=None):
        order = self.get_object()
        if not order.is_cancellable:
            return Response({'error':'cant cancel this order anymore'},status=status.HTTP_400_BAD_REQUEST)
        try:
            order.rreject()
            if order.driver:
                dp = order.driver.driver_profile
                dp.is_available = True
                dp.save(update_fields=['is_available'])
            return Response({'message':'order cancelled'})
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
    #=======================================
    # LIST ALL ACTIVE ORDERS
    @action(detail=False,methods=['get'],pagination_class=OrdersPagination)
    def active(self,request):
        qs = self.get_queryset().exclude(status__in=['dl','cd'])
        return Response(OrderSerializer(qs,many=True).data)
    #=======================================
    # LIST ALL ORDERS
    @action(detail=False,methods=['get'],pagination_class=OrdersPagination)
    def history(self,request):
        qs = self.get_queryset().filter(status__in=['dl','cd'])
        return Response(OrderSerializer(qs,many=True).data)

#===============================================================================================
# REVIEW VIEWSET
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    #throttle_classes = [ReviewCreateT]
    pagination_class = ReviewPagination

    def get_throttles(self):
        if self.action == 'create':
            return [ReviewCreateT()]
        return super().get_throttles()

    def get_queryset(self):
        qs = Review.objects.select_related('customer','restaurant','menu_item','order')
        restaurant_id = self.request.query_params.get('restaurant')
        if restaurant_id:
            qs = qs.filter(restaurant_id=restaurant_id)
        return qs

    def perform_create(self,serializer):
        serializer.save(customer=self.request.user)
        logger.info(f"===review created by {self.request.user.email}===")
