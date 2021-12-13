from pymongo import MongoClient
from bson.json_util import dumps

# Cloud function to get user summaries


def read_mongodb_user_summaries(request):
    client = MongoClient(
        "mongodb+srv://AD-DB-User:%26h8Xt2Q%23V%26SG@cluster0.pglda.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

    print("Connection successful to MongoDB version: " +
          client.server_info()['version'])

    db = client['BTEC-Furniture']['Users']

    print("Connection successful to collection")

    myCursor = None

    requestedData = {
        '_id': 0,
        'userId': 1,
        'email': 1,
        'name': 1,
        'admin': 1,
        'orders': 0,
        'basket': 0
    }

    myCursor = db.find({}, requestedData)
    list_items = list(myCursor)
    json_data = dumps(list_items)
    return json_data
