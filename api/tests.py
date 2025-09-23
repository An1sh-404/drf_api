# from django.test import TestCase
from api.models import Order, Product, User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
# Create your tests here.
# class UserOrderTestCase(TestCase):
#     def setUp(self):
#         user1 = User.objects.create_user(username='user1',password = 'test' )
#         user2 = User.objects.create_user(username='user2',password = 'test')
#         Order.objects.create(user=user1)
#         Order.objects.create(user=user1)
#         Order.objects.create(user=user2)
#         Order.objects.create(user=user2)
        
#     def test_user_order_endpoint_retrives_only_authenticated_user_orders(self):
#         user = User.objects.get(username = 'user2')
#         self.client.force_login(user)
#         response = self.client.get(reverse('user_order'))


#         assert response.status_code == status.HTTP_200_OK
#         orders = response.json()
#         # print(data)
#         self.assertTrue(all(order['user']==user.id for order in orders))


#     def test_user_order_list_unauthenticated(self):
#         response = self.client.get(reverse('user_order'))
#         # self.assertEqual(response.status_code,403)
#         self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
#class UserOrderTestCase(TestCase):
#     def setUp(self):
#         user1 = User.objects.create_user(username='user1',password = 'test' )
#         user2 = User.objects.create_user(username='user2',password = 'test')
#         Order.objects.create(user=user1)
#         Order.objects.create(user=user1)
#         Order.objects.create(user=user2)
#         Order.objects.create(user=user2)
        
#     def test_user_order_endpoint_retrives_only_authenticated_user_orders(self):
#         user = User.objects.get(username = 'user2')
#         self.client.force_login(user)
#         response = self.client.get(reverse('user_order'))


#         assert response.status_code == status.HTTP_200_OK
#         orders = response.json()
#         # print(data)
#         self.assertTrue(all(order['user']==user.id for order in orders))


#     def test_user_order_list_unauthenticated(self):
#         response = self.client.get(reverse('user_order'))
#         # self.assertEqual(response.status_code,403)
#         self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)

# tests for views

class ProductAPITestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(username='admin', password='adminpass')
        self.normal_user = User.objects.create_user(username='user', password='userpass')

        self.product = Product.objects.create(
            name="Test Product",
            description="Test Description",
            price=10.99,
            stock = 9
        )
        self.url = reverse('product_detail',kwargs={'product_id':self.product.pk})

    
    def test_get_product(self):
        response = self.client.get(self.url) # get is allowany
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.product.name)


    
    def test_unauthorized_update_product(self):
        data = {"name":"Updated Product"}
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) # Not authenticated i.e user credentails are not provided

    
    def test_unauthorized_delete_product(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)

    
    def test_only_admins_can_delete_product(self):
        # test normal user cannot delete -note that this could be its own method
        self.client.login(username='user', password='userpass')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN) # authenticated but not authorized, since only admin access is allowed so forbidden
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())
        
        # test admin user can delete
        self.client.login(username='admin', password='adminpass')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code,status.HTTP_204_NO_CONTENT) # authenticated but not authorized, since only admin access is allowed so forbidden
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())
        