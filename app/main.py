import logging
import requests
import datetime
import json
from flask import Flask, render_template, request, url_for, redirect

from google.auth.transport import requests as googleRequests
import google.oauth2.id_token

firebase_request_adapter = googleRequests.Request()

app = Flask(__name__)


def authenticateUser():
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
    id_token = request.cookies.get("token")
    error_message = None
    claims = "Test"  # TODO Remove before commit
    if id_token:
        try:
            # Verify the token against the Firebase Auth API.
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
            # Grab your auth sensitive data here
        except ValueError as exc:
            # Expired tokens etc
            error_message = str(exc)
    return {
        "user_data": claims,
        "error_message": error_message
    }


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


@app.route('/')
@app.route('/home')
def home():
    url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/mongodbdisplay"
    response = requests.get(url)
    product_info = formatProductData(
        json.loads(response.content.decode("utf-8")))
    return render_template('home.html', product_info=product_info)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/login')
def login():
    authContent = authenticateUser()

    # Return your page with any retrieved data (or return different pages if not logged in)
    return render_template(
        'login.html',
        user_data=authContent['user_data'],
        error_message=authContent['error_message'])


@app.route('/admin')
def form():
    authContent = authenticateUser()

    # If not authenticated
    if authContent['user_data'] == None:
        return redirect(url_for('login'))
    else:
        return render_template('admin.html',
                               user_data=authContent['user_data'],
                               error_message=authContent['error_message'])


@app.route('/submitted', methods=['POST'])
def submitted_form():
    authContent = authenticateUser()

    # If not authenticated
    if authContent['user_data'] == None:
        return redirect(url_for('login'))
    else:
        params = {
            "title": str(request.form['title']),
            "description": str(request.form['description']),
            "pricePerUnit": str(request.form['pricePerUnit']),
            "qty": int(request.form['qty']),
            "tags": request.form['tags']
        }

        url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/create_mongodb_product"
        response = requests.get(url, params)

        return render_template(
            'submitted_form.html',
            title=params['title'],
            description=params['description'],
            pricePerUnit=params['pricePerUnit'],
            qty=params['qty'],
            tags=params['tags'],
            user_data=authContent['user_data'],
            error_message=authContent['error_message'],
            response=response.content
        )


@app.errorhandler(500)
def server_error(error):
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    # Only run for local development.
    app.run(host='127.0.0.1', port=8080, debug=True)
