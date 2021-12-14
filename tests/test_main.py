import unittest
from unittest import mock
from types import SimpleNamespace
from app import main


class TestHTTPMethods(unittest.TestCase):

    # Create a test local Flask client
    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()

    def unauthenticatedUserHelper(token):
        return {
            'user_data': None,
            'error_message': 'An authentication error message'
        }

    def authenticatedUserHelper(token):
        return {
            'user_data': {
                'userId': '3FCEQ8ZzLjXsmQwv9Yc8Q4oYOfp1',
                'email': '123@gmail.com',
                'name': 'Mr 123',
                'admin': False,
                'orders': [{
                    'timestamp': '2021-12-13 15:07:02.188034',
                    'name': 'Mr 123',
                    'address': 'Picket Lane',
                    'paymentType': 'card',
                    'content': [{
                        'productId': '619bb55c11dd33ac12d5aa0f',
                        'qty': '2'
                    }],
                    'expectedDeliveryDate': '2021-12-20 15:07:02.191293',
                    'totalCost': '400.5',
                    'status': 'Cancelled'
                }],
                'basket': [{
                    'productId': '619bb55c11dd33ac12d5aa12',
                    'qty': '8'
                }]
            },
            'error_message': 'An authentication error message'
        }

    def adminUserHelper(token):
        user = TestHTTPMethods.authenticatedUserHelper(token)
        user['admin'] = True
        return user

    def addToBasketHelper(userId, productId, qty):
        return 201

    def removeFromBasketHelper(userId, basketIndex):
        return 201

    def test_root(self):
        response = self.app.get('/')
        self.assertIn("<h1>Welcome to BTEC Furniture </h1>",
                      str(response.data))
        self.assertEqual(response.status_code, 200)

    def test_home(self):
        response = self.app.get('/home')
        self.assertIn("<h1>Welcome to BTEC Furniture </h1>",
                      str(response.data))
        self.assertEqual(response.status_code, 200)

    def test_about(self):
        response = self.app.get('/about')
        self.assertIn("BTECFurniture@gmail.com",
                      str(response.data))
        self.assertEqual(response.status_code, 200)

    @mock.patch('tools.authenticateUser', unauthenticatedUserHelper)
    def test_login(self):
        response = self.app.get('/login')
        self.assertIn('<div id="firebaseui-auth-container">',
                      str(response.data))
        self.assertEqual(response.status_code, 200)

    @mock.patch('tools.authenticateUser', unauthenticatedUserHelper)
    def test_basket_not_logged_in(self):
        response = self.app.get('/basket')
        self.assertIn('You should be redirected automatically to target URL: <a href="/login">/login</a>',
                      str(response.data))
        self.assertEqual(response.status_code, 302)

    @mock.patch('tools.authenticateUser', authenticatedUserHelper)
    def test_basket_logged_in(self):
        response = self.app.get('/basket')
        self.assertIn('Basket value:',
                      str(response.data))
        self.assertEqual(response.status_code, 200)

    @mock.patch('tools.addToBasket', addToBasketHelper)
    @mock.patch('tools.authenticateUser', unauthenticatedUserHelper)
    def test_add_to_basket_not_logged_in(self):
        response = self.app.post('/add_to_basket', data=dict(
            id='619bb55c11dd33ac12d5aa12',
            qty='5'
        ))
        self.assertIn('You should be redirected automatically to target URL: <a href="/login">/login</a>',
                      str(response.data))
        self.assertEqual(response.status_code, 302)

    @mock.patch('tools.addToBasket', addToBasketHelper)
    @mock.patch('tools.authenticateUser', authenticatedUserHelper)
    def test_add_to_basket_logged_in(self):
        response = self.app.post('/add_to_basket', data=dict(
            id='619bb55c11dd33ac12d5aa12',
            qty='5'
        ))
        self.assertIn('Success', str(response.data))
        self.assertEqual(response.status_code, 201)

    @mock.patch('tools.removeFromBasket', removeFromBasketHelper)
    @mock.patch('tools.authenticateUser', unauthenticatedUserHelper)
    def test_remove_from_basket_not_logged_in(self):
        response = self.app.post(
            '/remove_from_basket', data=dict(basketIndex='0'))
        self.assertIn('You should be redirected automatically to target URL: <a href="/login">/login</a>',
                      str(response.data))
        self.assertEqual(response.status_code, 302)

    @mock.patch('tools.removeFromBasket', removeFromBasketHelper)
    @mock.patch('tools.authenticateUser', authenticatedUserHelper)
    def test_remove_from_basket_logged_in(self):
        response = self.app.post(
            '/remove_from_basket', data=dict(basketIndex='0'))
        self.assertIn('You should be redirected automatically to target URL: <a href="/basket">/basket</a>',
                      str(response.data))
        self.assertEqual(response.status_code, 302)

    @mock.patch('tools.authenticateUser', unauthenticatedUserHelper)
    def test_orders_not_logged_in(self):
        response = self.app.get('/orders')
        self.assertIn('You should be redirected automatically to target URL: <a href="/login">/login</a>',
                      str(response.data))
        self.assertEqual(response.status_code, 302)

    @mock.patch('tools.authenticateUser', authenticatedUserHelper)
    def test_orders_logged_in(self):
        response = self.app.get('/orders')
        self.assertIn('2021-12-13',  # Timestamp of the order saved on the user
                      str(response.data))
        self.assertEqual(response.status_code, 200)

    @mock.patch('tools.authenticateUser', unauthenticatedUserHelper)
    def test_create_order_not_logged_in(self):
        response = self.app.get('/create_order')
        self.assertIn('You should be redirected automatically to target URL: <a href="/login">/login</a>',
                      str(response.data))
        self.assertEqual(response.status_code, 302)

    @mock.patch('tools.authenticateUser', authenticatedUserHelper)
    def test_create_order_logged_in(self):
        response = self.app.get('/create_order')
        self.assertIn('<button type="submit" class="btn btn-success">Submit Order</button>',
                      str(response.data))
        self.assertEqual(response.status_code, 200)

    def test_404(self):
        response = self.app.get('/notavalidroute')
        self.assertIn('The requested URL was not found on the server',
                      str(response.data))
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
