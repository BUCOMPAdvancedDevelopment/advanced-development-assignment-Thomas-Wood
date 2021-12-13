from pymongo import MongoClient

# Cloud function to delete users in mongo


def delete_mongodb_user(request):
    client = MongoClient(
        "mongodb+srv://AD-DB-User:%26h8Xt2Q%23V%26SG@cluster0.pglda.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

    print("Connection successful to MongoDB version: " +
          client.server_info()['version'])

    db = client['BTEC-Furniture']['Users']

    print("Connection successful to collection")

    myquery = {"userId": request.form['userId']}

    db.delete_one(myquery)

    return '201'
