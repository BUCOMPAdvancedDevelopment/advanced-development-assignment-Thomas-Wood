from pymongo import MongoClient
from bson.json_util import dumps

# Cloud function to get user details from mongo


def read_mongodb_user(request):
    client = MongoClient(
        "mongodb+srv://AD-DB-User:%26h8Xt2Q%23V%26SG@cluster0.pglda.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

    print("Connection successful to MongoDB version: " +
          client.server_info()['version'])

    db = client['BTEC-Furniture']['Users']

    print("Connection successful to collection")

    myCursor = None

    userId = request.args['id']

    print("Attempting to access ID: " + userId)
    myquery = {"userId": userId}
    myCursor = db.find_one(myquery)

    if myCursor is None:
        # Create an account
        print("Account not found, create account")
        data = {
            'email': request.args['email'],
            'name': request.args['name'],
            'admin': False,
            'orders': [],
            'basket': []
        }
        result = db.insert_one(data)

        # Get the new account
        myCursor = db.find_one(myquery)

    json_data = dumps(myCursor)
    return json_data
