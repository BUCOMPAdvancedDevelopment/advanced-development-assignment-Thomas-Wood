import json
import google.oauth2.id_token
from google.auth.transport import requests as googleRequests
import requests

firebase_request_adapter = googleRequests.Request()


def formatProductData(products):
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
    """ Claims contains the following attributes:
    name: '{string}'
    picture: '{url}'
    iss: 'https://securetoken.google.com/{project name}'
    aud: '{project name}'
    auth_time: '{time you authenticated at}'
    user_id: '{Long string}'
    sub: '{long string same as user_id, maybe for sub-accounts}'
    iat: {Login started at}
    exp: {Login expires at}
    email: {user's email address}
    email_verified: {Boolean}
    firebase: {identities: 
                {'google.com': ['{Long number}'],
                'email': ['{user's email address}']},
              'sign_in_provider': 'google.com'}}
    """

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
    url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/read_mongodb_users"
    data = {
        'userId': userId,
        'email': email,
        'name': name
    }
    response = requests.get(url, data)
    user_data = json.loads(response.content.decode("utf-8"))

    return user_data


def getProduct(productId):
    url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/read_mongodb_products"
    response = requests.get(url, {'id': productId})
    data = json.loads(response.content.decode("utf-8"))
    return data
