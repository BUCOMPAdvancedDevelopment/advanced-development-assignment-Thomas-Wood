from pymongo import MongoClient
from flask import request

# Cloud function to create products in mongo


def create_mongodb_product(request):
    client = MongoClient(
        "mongodb+srv://AD-DB-User:%26h8Xt2Q%23V%26SG@cluster0.pglda.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

    print("Connection successful to MongoDB version: " +
          client.server_info()['version'])

    db = client['BTEC-Furniture']['Products']

    print("Connection successful to collection")

    product_data = {
        "title": str(request.args['title']),
        "description": str(request.args['description']),
        "pricePerUnit": str(request.args['pricePerUnit']),
        "qty": int(request.args['qty']),
        "imageID": str(request.args['imageID']),
        "tags": request.args['tags']
    }

    result = db.insert_one(product_data)

    print("Created object with ID: " + str(result.inserted_id))

    return str(result.inserted_id)
