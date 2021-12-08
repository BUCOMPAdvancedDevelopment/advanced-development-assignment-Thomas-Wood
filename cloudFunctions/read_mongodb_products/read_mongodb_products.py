from pymongo import MongoClient
from bson.json_util import dumps
from bson import ObjectId

# Cloud function to get product details from mongo


def read_mongodb_products(request):
    client = MongoClient(
        "mongodb+srv://AD-DB-User:%26h8Xt2Q%23V%26SG@cluster0.pglda.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

    print("Connection successful to MongoDB version: " +
          client.server_info()['version'])

    db = client['BTEC-Furniture']['Products']

    print("Connection successful to collection")

    myCursor = None

    try:
        id = request.args['id']
    except:
        id = False

    if id:  # Return a particular product
        myquery = {"_id": ObjectId(id)}
        myCursor = db.find_one(myquery)
        json_data = dumps(myCursor)
        return json_data
    else:  # Return all products
        myCursor = db.find()
        list_items = list(myCursor)
        json_data = dumps(list_items)
        return json_data
