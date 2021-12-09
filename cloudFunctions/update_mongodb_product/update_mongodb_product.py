from pymongo import MongoClient
from bson import ObjectId
from flask import request

# Cloud function to update products in mongo


def update_mongodb_product(request):
    client = MongoClient(
        "mongodb+srv://AD-DB-User:%26h8Xt2Q%23V%26SG@cluster0.pglda.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

    print("Connection successful to MongoDB version: " +
          client.server_info()['version'])

    db = client['BTEC-Furniture']['Products']

    print("Connection successful to collection")

    data_to_change = {}

    if request.args['title']:
        data_to_change.update({'title': request.args['title']})
    if request.args['description']:
        data_to_change.update({'description': request.args['description']})
    if request.args['pricePerUnit']:
        data_to_change.update({'pricePerUnit': request.args['pricePerUnit']})
    if request.args['qty']:
        data_to_change.update({'qty': request.args['qty']})
    if request.args['tags']:
        data_to_change.update({'tags': request.args['tags'].strip(',')})

    myquery = {"_id": ObjectId(request.args['id'])}
    newvalues = {"$set": data_to_change}

    db.update_one(myquery, newvalues)

    return '201'
