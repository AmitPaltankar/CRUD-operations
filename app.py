from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from marshmallow import Schema, fields, ValidationError
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Product {self.id}>'

# Product schema for validation
class ProductSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    price = fields.Float(required=True)


# Example GET request to obtain JWT token
# response = requests.get('http://localhost:5000/generate_token')

#Routes for get jwt token
@app.route('/generate_token', methods=['GET'])
def generate_jwt_token():
    try:
        token = create_access_token(identity='some_identity')
        return jsonify(access_token=token), 200
    except Exception as e:
        app.logger.error(f"Exception occurred in generate_jwt_token endpoint: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

#Routes for get all data
@app.route('/products', methods=['GET'])
@jwt_required()     #authentication of token
def get_products():
    try:
        # Get query parameters for pagination
        # limit = request.args.get('limit', 5, type=int)  # Default limit is 5
        # page = request.args.get('page', 2, type=int)    # Default page is 1

        per_page = request.args.get('per_page', 5, type=int)

        # Calculate the number of items to skip based on the page number
        # skip = (page - 1) * limit

        # Fetch products from the database with pagination
        # products = Product.query.offset(0).limit(limit).all()
        # products = Product.query.paginate(page=page, per_page=per_page, error_out=False)
        Total_product_pages = []
        if Product.query.count()%5 != 0:
            pageCount = (Product.query.count()//5) + 1
        else:
            pageCount  =Product.query.count()//5
            
        for i in range(1,pageCount+1):
            products = Product.query.paginate(page=i, per_page=per_page, error_out=False)
            # print(pageCount)
            serialized_products = []
            total_items = 0
            for product in products:
                total_items += 1
                serialized_product = {
                    'id': product.id,
                    'title': product.title,
                    'description': product.description,
                    'price': product.price
                }
                serialized_products.append(serialized_product)
            response = {
            'page': products.page,
            'per_page': products.per_page,
            'total_pages': products.pages,
            'total_items_in_page': total_items,
            'products': serialized_products
            }
            Total_product_pages.append(response)
        return jsonify(Total_product_pages), 200
    except Exception as e:
        app.logger.error(f"Exception occurred in get_products endpoint: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

#Routes for get data based on id
@app.route('/products/<int:product_id>', methods=['GET'])
@jwt_required()       #authentication of token
def get_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        serialized_product = {
            'id': product.id,
            'title': product.title,
            'description': product.description,
            'price': product.price
        }
        return jsonify(serialized_product)
    except Exception as e:
        app.logger.error(f"Exception occurred in get_products endpoint: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

#Routes for adding the data to the DB
@app.route('/products', methods=['POST'])
@jwt_required()       #authentication of token
def create_product():
    try:
        data = request.json
        product_schema = ProductSchema()
        product = product_schema.load(data)
        new_product = Product(**product)
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'message': 'Product created successfully'}), 201
    except ValidationError as e:
        app.logger.error(f"Exception occurred in create_product endpoint: {e}")
        return jsonify({'error': e.messages}), 400

#Routes for updating the data to the DB based on the id
@app.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required() #authentication of token
def update_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        data = request.json
        product_schema = ProductSchema()
        updated_product = product_schema.load(data)
        for key, value in updated_product.items():
            setattr(product, key, value)
        db.session.commit()
        return jsonify({'message': 'Product updated successfully'})
    except ValidationError as e:
        app.logger.error(f"Exception occurred in update_product product_id:{product_id} endpoint: {e}")
        return jsonify({'error': e.messages}), 400

#Routes for deleting the data based on the id
@app.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()      #authentication of token
def delete_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'})
    except Exception as e:
        app.logger.error(f"Exception occurred in delete_product product_id:{product_id} endpoint: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500


# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
