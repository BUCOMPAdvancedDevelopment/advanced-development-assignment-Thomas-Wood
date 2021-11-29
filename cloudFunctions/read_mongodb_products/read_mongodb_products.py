from pymongo import MongoClient
from bson.json_util import dumps
from flask import Blueprint, request, jsonify
import os
import requests
import json

# Cloud function to get product details from mongo


def read_mongodb_products(request):
    client = MongoClient(
        "mongodb+srv://AD-DB-User:%26h8Xt2Q%23V%26SG@cluster0.pglda.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

    try:
        print("Connection successful to MongoDB version: " +
              client.server_info()['version'])
    except Exception:
        print("Unable to connect to the server.")

    db = client['BTEC-Furniture']['Products']

    print("Connection successful to collection")

    myCursor = None

    # create queries
    #title_query = {"title": {"$eq": "Man walks on the moon"}}
    #author_query = {"author": {"$eq": "Faker"}}
    #dateCreated_query = {"dateCreated": {"$eq": 2019}}
    #myCursor = db.find(title_query)

    myCursor = db.find()
    list_items = list(myCursor)
    json_data = dumps(list_items)
    return json_data
