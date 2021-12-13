import json
import google.oauth2.id_token
from google.auth.transport import requests as googleRequests
import requests

firebase_request_adapter = googleRequests.Request()


def formatProductData(products):
    """Formats a list of products into rows of three products long"""
    newFormat = []
    currentRow = []
    for product in products:
        currentRow.append(product)
        if len(currentRow) == 3:
            newFormat.append(currentRow)
            currentRow = []
    if len(currentRow) != 0:
        newFormat.append(currentRow)
    return newFormat


def authenticateUser(token):
    """ Authenticates the user and returns the user's information"""

    # Verify Firebase auth.
    id_token = token
    error_message = None
    claims = None
    user_data = None
    if id_token:
        try:
            # Verify the token against the Firebase Auth API.
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)

            # Get the users' account (and make it if it doesn't exist)
            user_data = getUserData(
                claims['user_id'], claims['email'], claims['name'])

        except ValueError as exc:
            # Expired tokens etc
            error_message = str(exc)
            user_data = None
    return {
        "user_data": user_data,
        "error_message": error_message
    }


def getUserData(userId, email="", name=""):
    """Get's the specified user's account including basket and orders.
    If the userId is not in the database, an account will be created for it.
    """

    url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/read_mongodb_users"
    data = {
        'userId': userId,
        'email': email,
        'name': name
    }
    response = requests.get(url, data)
    user_data = json.loads(response.content.decode("utf-8"))

    return user_data


def getProduct(productId=None):
    """Returns information on products
    If productId is supplied, just that product will be returned.
    If no productId is supplied, all products are returned.
    """

    url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/read_mongodb_products"

    if productId:
        params = {'id': productId}
    else:
        params = {}

    response = requests.get(url, params)
    data = json.loads(response.content.decode("utf-8"))
    return data


def addToBasket(userId, productId, qty):
    """Adds a number of products to a specified user's basket
    On success, returns 201
    """

    url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/add_mongodb_user_basket"
    params = {
        "userId": userId,
        "productId": productId,
        "qty": qty
    }
    response = requests.post(
        url, params)

    return response.status_code


def removeFromBasket(userId, basketIndex):
    """Removes a product from a specified user's basket
    On success, returns 201
    """

    url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/remove_mongodb_user_basket"
    params = {
        "userId": userId,
        "basketIndex": basketIndex
    }
    response = requests.post(
        url, params)

    return response.status_code


def createOrder(orderDetails):
    """Creates and order and empties the basket in a user's account
    On success, returns 201
    """

    url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/add_mongodb_user_order"
    response = requests.post(url, orderDetails)

    return response.status_code


def getUserSummaries():
    """Gets all user's id, email, name and admin status"""

    url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/read_mongodb_user_summaries"
    response = requests.get(url)
    customer_data = json.loads(response.content.decode("utf-8"))

    return customer_data


def deleteUser(userId):
    """Deletes a user's account from the database
    On success, returns 200
    """
    url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/delete_mongodb_user"
    response = requests.post(url, {'userId': userId})

    return response.status_code


def updateUser(params):
    """Updates a user's account
    On success, returns 200
    """
    url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/update_mongodb_user"
    response = requests.post(url, params)

    return response.status_code


def createProduct(params):
    """Creates a new product in Mongo (Text part)
    On success, returns 200
    """
    url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/create_mongodb_product"
    response = requests.get(url, params)

    return response.status_code


def uploadImage(imageId, base64Image):
    """Creates a new product image in Cloud Storage
    On success, returns 200
    """
    url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/upload_cloud_storage_image"
    params = {
        "id": imageId,
        "image": base64Image
    }
    response = requests.post(url, params)

    return response.status_code


def deleteImage(id):
    """Deletes a product image in Cloud Storage
    On success, returns 200
    """
    url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/delete_cloud_storage_image"
    response = requests.post(url, {"id": id})

    return response.status_code


def updateProduct(params):
    """Updates a products text in Mongo
    On success, returns 200
    """
    url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/update_mongodb_product"
    response = requests.get(url, params)

    return response.status_code


def deleteProduct(id):
    """Deletes a product in Mongo
    On success, returns 200
    """
    url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/delete_mongodb_product"
    response = requests.get(url, {"id": id})

    return response.status_code
