from pymongo import MongoClient

# Cloud function to update users in mongo


def update_mongodb_user(request):
    client = MongoClient(
        "mongodb+srv://AD-DB-User:%26h8Xt2Q%23V%26SG@cluster0.pglda.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

    print("Connection successful to MongoDB version: " +
          client.server_info()['version'])

    db = client['BTEC-Furniture']['Users']

    print("Connection successful to collection")

    myquery = {"userId": request.form['userId']}

    orders = db.find_one(myquery)['orders']

    statusListIndex = 0
    for order in orders:
        order['status'] = request.form['orderStatuses'][statusListIndex]
        statusListIndex += 1

    data_to_change = {
        'name': request.form['name'],
        'admin': request.form['admin'],
        'orders': orders
    }

    newvalues = {"$set": data_to_change}

    db.update_one(myquery, newvalues)

    return '201'
