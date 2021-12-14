import unittest
from unittest import mock
from types import SimpleNamespace
from app import main


class TestHTTPMethods(unittest.TestCase):

    # Create a test local Flask client
    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()

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
        self.assertIn("contact details",
                      str(response.data))
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        response = self.app.get('/login')
        self.assertIn('<div id="firebaseui-auth-container">',
                      str(response.data))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.app.get('/post')
        self.assertIn('<input type="submit">',
                      str(response.data))
        self.assertEqual(response.status_code, 200)

    @mock.patch('requests.get', lambda url, params: SimpleNamespace(content=201))
    def test_submitted(self):
        response = self.app.post('/submitted', data=dict(
            title='Test',
            author='Test',
            content='Test'
        ))
        self.assertIn('201',
                      str(response.data))
        self.assertEqual(response.status_code, 200)

    def test_404(self):
        response = self.app.get('/notavalidroute')
        self.assertIn('The requested URL was not found on the server',
                      str(response.data))
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
