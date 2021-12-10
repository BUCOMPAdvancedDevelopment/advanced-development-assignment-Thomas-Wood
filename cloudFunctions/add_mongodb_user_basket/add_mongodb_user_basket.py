from pymongo import MongoClient
from bson.json_util import dumps

# Cloud function to add product to basket


def add_mongodb_user_basket(request):
    client = MongoClient(
        "mongodb+srv://AD-DB-User:%26h8Xt2Q%23V%26SG@cluster0.pglda.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

    print("Connection successful to MongoDB version: " +
          client.server_info()['version'])

    db = client['BTEC-Furniture']['Users']

    print("Connection successful to collection")

    userId = request.form['userId']

    productDetails = {
        'productId': request.form['productId'],
        'qty': request.form['qty']
    }

    myquery = {"userId": userId}
    basket = db.find_one(myquery)['basket']

    basket.append(productDetails)

    newValues = {"$set": {"basket": basket}}

    response = db.update_one(myquery, newValues)

    return "Updated basket", 201
