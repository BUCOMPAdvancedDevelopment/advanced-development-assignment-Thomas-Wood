import logging
import requests
import datetime
from flask import Flask, render_template, request

from google.auth.transport import requests as googleRequests
import google.oauth2.id_token

firebase_request_adapter = googleRequests.Request()

app = Flask(__name__)

# def hello():
#     url= "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/hellow-world"
#     response=requests.get(url)
#     return(response.content)


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
    claims = None
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


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


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


@app.route('/post')
def form():
    authContent = authenticateUser()

    return render_template('post.html',
                           user_data=authContent['user_data'],
                           error_message=authContent['error_message'])


@app.route('/submitted', methods=['POST'])
def submitted_form():
    authContent = authenticateUser()

    params = {
        'title': request.form['title'],
        'author': request.form['author'],
        'content': request.form['content'],
        'currentDate': datetime.datetime.now().strftime("%Y/%m/%d")
    }

    url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/mongodbpost"
    response = requests.get(url, params)

    return render_template(
        'submitted_form.html',
        title=params['title'],
        author=params['author'],
        content=params['content'],
        date=params['currentDate'],
        user_data=authContent['user_data'],
        error_message=authContent['error_message'],
        response=response.content
    )


@app.errorhandler(500)
def server_error(error):
    # Log the error and stacktrace.
    print("500 error occured:")
    print(error)
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500


@app.errorhandler(404)
def page_not_found(error):
    print("404 error occured:")
    print(error)
    return render_template('404.html'), 404


if __name__ == '__main__':
    # Only run for local development.
    app.run(host='127.0.0.1', port=8080, debug=True)
