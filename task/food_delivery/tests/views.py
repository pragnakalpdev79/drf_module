import pytest
from django.contrib.auth.models import Group


import pytest
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import Group,Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIClient
from rest_framework import status
from user.models import *


# #===============================================================================
# #===============================================================================
# # FIXTURES - creating test data that all tests will use
# #===============================================================================

@pytest.fixture(autouse=True)
def create_groups(db):
    cgrps,created = Group.objects.get_or_create(name='Customers')
    Group.objects.get_or_create(name='RestrauntOwners')
    Group.objects.get_or_create(name='Drivers')
    print("groups created for test")
    content_type = ContentType.objects.get_for_model(CustomUser)
    customer_permissions = Permission.objects.filter(content_type=content_type,
                                                     codename__in =['IsCustomer'])
    cgrps.permissions.set(customer_permissions)
    

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def customer(db):
    user = CustomUser.objects.create_user(
        email='testcust@test.com',
        password='testpass123',
        username='testcust',
        first_name='Test',
        last_name='Customer',
        phone_number='+919999999990',
        utype='c'
    )
    print(f"created customer -- {user.has_perms}")
    grp = Group.objects.get(name='Customers')
    print(grp.permissions.all())
    user.groups.add(grp)
    return user

@pytest.fixture
def resto_owner(db):
    user = CustomUser.objects.create_user(
        email='testowner@test.com',
        password='testpass123',
        username='testowner',
        first_name='Test',
        last_name='Owner',
        phone_number='+919999999991',
        utype='r'
    )
    print(f"created resto owner -- {user}")
    
    return user

@pytest.fixture
def driver(db):
    user = CustomUser.objects.create_user(
        email='testdriver@test.com',
        password='testpass123',
        username='testdriver',
        first_name='Test',
        last_name='Driver',
        phone_number='+919999999992',
        utype='d'
    )

    print(f"created driver -- {user}")
    return user

@pytest.fixture
def restaurant(db,resto_owner):
    resto = RestrauntModel.objects.create(
        owner=resto_owner,
        name='Test Indianresto',
        description='testing food',
        cuisine_type='in',
        address='123 test Gandhinagar',
        phone_number='+918888888885',
        email='resto@test.com',
        opening_time='09:00:00',
        closing_time='23:00:00',
        is_open=True,
        delivery_fee=Decimal('30.00'),
        minimum_order=Decimal('100'),
    )
    print(f"created restaurant -- {resto}")
    return resto

@pytest.fixture
def menu_items(db,restaurant):
    item1 = MenuItem.objects.create(
        restaurant=restaurant,
        name='Paneer Butter Masala',
        description='paneer',
        price=Decimal('250.00'),
        category='m',
        dietary_info='v1',
        is_available=True,
    )
    item2 = MenuItem.objects.create(
        restaurant=restaurant,
        name='Dal Tadka',
        description='dal with tadka',
        price=Decimal('150.00'),
        category='m',
        dietary_info='v1',
        is_available=True,
    )
    item3 = MenuItem.objects.create(
        restaurant=restaurant,
        name='Gulab Jamun',
        description='dessert',
        price=Decimal('80.00'),
        category='d',
        dietary_info='no',
        is_available=False,
    )
    print(f"created 3 menu items for {restaurant.name}")
    return [item1,item2,item3]

@pytest.fixture
def customer_with_address(db,customer):
    #creating address for checkout
    adr = address.objects.create(
        adrname='Home',
        address='q123 adr ahmedbad',
        is_default=True,
        adrofuser=customer
    )
    print(f"address set for {customer.email} -- {adr}")
    return customer

# #===============================================================================
# #===============================================================================
# # 1. REGISTRATION TESTS
# #===============================================================================

@pytest.mark.django_db
class TestRegistration:
    #NORMAL REGISTRATION
    def test_customer_registration(self,api_client):
        print("=====test1 registration=====")
        data = {
            'email':'newcust@test.com',
            'username':'newcust',
            'password':'strongpass123',
            'password_confirm':'strongpass123',
            'first_name':'New',
            'last_name':'Customer',
            'phone_number':'+911234567890',
            'utype':'c'
        }
        response = api_client.post('/api/auth/register/',data,format='json')
        print(f"response -- {response.status_code}")
        print(response)
        assert response.status_code == 201
        assert 'access' in response.data
        assert 'refresh' in response.data
    #PASSWORD MISMATCH
    def test_registration_password_mismatch(self,api_client):
        print("=====test2 password mismatch=====")
        data = {
            'email':'fail@test.com',
            'username':'failuser',
            'password':'spass123',
            'password_confirm':'wpass123',
            'first_name':'Fail',
            'last_name':'User',
            'phone_number':'+911234567890',
            'utype':'c'
        }
        response = api_client.post('/api/auth/register/',data,format='json')
        print(f"response -- {response.status_code}")
        assert response.status_code == 400
    #DUPLICATE EMAIL
    def test_registration_duplicate_email(self,api_client,customer):
        print("=====test3 duplicate email=====")
        data = {
            'email':'testcust@test.com', #already exists
            'username':'anothercust',
            'password':'strongpass123',
            'password_confirm':'strongpass123',
            'first_name':'Another',
            'last_name':'Customer',
            'phone_number':'+911234567890',
            'utype':'c'
        }
        response = api_client.post('/api/auth/register/',data,format='json')
        print(f"response -- {response.status_code}")
        assert response.status_code == 400

#===============================================================================
# 2. CART TESTS
#===============================================================================

@pytest.mark.django_db
class TestCart:
    def test_add_to_cart(self,api_client,customer,menu_items,create_groups):
        print("=====test4 add to cart=====")
        api_client.force_authenticate(user=customer)
        #print(customer.check_if_customer)
        print(customer.user_permissions) 
        print(customer.has_perm('user.IsCustomer'))
        print(menu_items[1].id)
        data = {'menu_item':menu_items[1].id,'quantity':2}
        print(data)
        response = api_client.post('/api/orders/cart/addtocart/',data,format='json')
        print(f"response -- {response.status_code}")
        print(response)
        assert response.status_code == 202
        assert response.data['message'] == 'item added to cart'

    def test_add_unavailable_item(self,api_client,customer,menu_items):
        print("=====test5 unavailable item=====")
        api_client.force_authenticate(user=customer)
        data = {'menu_item':menu_items[2].id,'quantity':1} #gulab jamun is unavailable
        print(data)
        response = api_client.post('/api/orders/cart/addtocart/',data,format='json')
        print(response)
        print(f"response -- {response.status_code}")
        assert response.status_code == 404
        assert 'not available' in response.data['error']















