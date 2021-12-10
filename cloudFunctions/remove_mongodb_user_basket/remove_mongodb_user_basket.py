from pymongo import MongoClient

# Cloud function to remove item from basket


def remove_mongodb_user_basket(request):
    client = MongoClient(
        "mongodb+srv://AD-DB-User:%26h8Xt2Q%23V%26SG@cluster0.pglda.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

    print("Connection successful to MongoDB version: " +
          client.server_info()['version'])

    db = client['BTEC-Furniture']['Users']

    print("Connection successful to collection")

    userId = request.form['userId']
    basketIndex = request.form['basketIndex']

    myquery = {"userId": userId}
    basket = db.find_one(myquery)['basket']

    del basket[basketIndex]

    newValues = {"$set": {"basket": basket}}

    response = db.update_one(myquery, newValues)

    return "Updated basket", 201
