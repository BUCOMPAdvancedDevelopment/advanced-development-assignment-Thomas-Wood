from pymongo import MongoClient
from bson import ObjectId
from flask import request

# Cloud function to delete products in mongo


def delete_mongodb_product(request):
    client = MongoClient(
        "mongodb+srv://AD-DB-User:%26h8Xt2Q%23V%26SG@cluster0.pglda.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

    print("Connection successful to MongoDB version: " +
          client.server_info()['version'])

    db = client['BTEC-Furniture']['Products']

    print("Connection successful to collection")

    myquery = {"_id": ObjectId(request.args['id'])}

    db.delete_one(myquery)

    return '201'
