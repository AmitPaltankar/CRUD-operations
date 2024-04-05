import unittest
from flask import Flask,request
import json
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from app import app, db, generate_jwt_token, Product # Import your Flask app and JWT token generation function

class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['JWT_SECRET_KEY'] = 'test-secret'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_generate_jwt_token(self):
        # Test token generation with valid identity
        token, error = generate_jwt_token()
        self.assertIsNotNone(token)
        self.assertIsNone(error)

        # Test token generation with invalid identity
        token, error = generate_jwt_token()
        self.assertIsNone(token)
        self.assertIsNotNone(error)

    def test_generate_token_endpoint(self):
        # Test POST request to generate token endpoint with valid identity
        response = self.app.post('/generate_token', json={'identity': 'test_identity'})
        data = response.get_json()
        self.assertEqual(response.status_code, 405)
        self.assertIn('token', data)

        # Test POST request to generate token endpoint with invalid identity
        response = self.app.post('/generate_token', json={})
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
    
    def test_get_all_products(self):
        # Insert sample products into the database
        # (You may need to adjust this based on your actual models)
        product1 = Product(title='Product 1', description='Description 1', price=10.99)
        product2 = Product(title='Product 2', description='Description 2', price=20.99)
        db.session.add_all([product1, product2])
        db.session.commit()

        # Make a GET request to /products
        response = self.app.get('/products')
        data = json.loads(response.data)

        # Assert status code and response content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 2)  # Assuming two products are returned

    def test_get_product_by_id(self):
        # Insert a sample product into the database
        product = Product(title='Product 1', description='Description 1', price=10.99)
        db.session.add(product)
        db.session.commit()

        # Make a GET request to /products/{id}
        response = self.app.get('/products/1')
        data = json.loads(response.data)

        # Assert status code and response content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['title'], 'Product 1')

    def test_create_product(self):
        # Make a POST request to create a new product
        product_data = {'title': 'New Product', 'description': 'New Description', 'price': 30.99}
        response = self.app.post('/products', json=product_data)
        data = json.loads(response.data)

        # Assert status code and response content
        self.assertEqual(response.status_code, 401)  # Assuming you return HTTP status code 201 for successful creation
        self.assertEqual(data['title'], 'New Product')

    def test_update_product(self):
        # Insert a sample product into the database
        product = Product(title='Product 1', description='Description 1', price=10.99)
        db.session.add(product)
        db.session.commit()

        # Make a PUT request to update the product
        updated_data = {'title': 'Updated Product', 'description': 'Updated Description', 'price': 15.99}
        response = self.app.put('/products/1', json=updated_data)
        data = json.loads(response.data)

        # Assert status code and response content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['title'], 'Updated Product')

    def test_delete_product(self):
        # Insert a sample product into the database
        product = Product(title='Product 1', description='Description 1', price=10.99)
        db.session.add(product)
        db.session.commit()

        # Make a DELETE request to delete the product
        response = self.app.delete('/products/1')

        # Assert status code
        self.assertEqual(response.status_code, 204) 

if __name__ == '__main__':
    unittest.main()
