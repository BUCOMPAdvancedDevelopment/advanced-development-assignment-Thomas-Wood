import logging
import requests
import json
from flask import Flask, render_template, request, url_for, redirect
import tools

app = Flask(__name__)


@app.route('/')
@app.route('/home')
def home():
    url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/mongodbdisplay"
    response = requests.get(url)
    product_info = tools.formatProductData(
        json.loads(response.content.decode("utf-8")))
    return render_template('home.html', product_info=product_info)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/login')
def login():
    authContent = tools.authenticateUser(request.cookies.get("token"))

    # Return your page with any retrieved data (or return different pages if not logged in)
    return render_template(
        'login.html',
        user_data=authContent['user_data'],
        error_message=authContent['error_message'])


@app.route('/admin')
def form():
    authContent = tools.authenticateUser(request.cookies.get("token"))

    # If not authenticated
    if authContent['user_data'] == None:
        return redirect(url_for('login'))
    else:
        url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/mongodbdisplay"
        response = requests.get(url)
        product_info = json.loads(response.content.decode("utf-8"))
        return render_template('admin.html',
                               product_info=product_info,
                               user_data=authContent['user_data'],
                               error_message=authContent['error_message'])


@app.route('/create_product_submitted', methods=['POST'])
def create_product_submitted_form():
    authContent = tools.authenticateUser(request.cookies.get("token"))

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


@app.route('/update_product_submitted', methods=['POST'])
def update_product_submitted_form():
    authContent = tools.authenticateUser(request.cookies.get("token"))

    # If not authenticated
    if authContent['user_data'] == None:
        return redirect(url_for('login'))
    else:
        params = {
            "id": str(request.form['id']),
            "title": str(request.form['title']),
            "description": str(request.form['description']),
            "pricePerUnit": str(request.form['pricePerUnit']),
            "qty": int(request.form['qty']),
            "tags": request.form['tags']
        }

        url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/update_mongodb_product"
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


@app.route('/delete_product_submitted', methods=['POST'])
def delete_product_submitted_form():
    authContent = tools.authenticateUser(request.cookies.get("token"))

    # If not authenticated
    if authContent['user_data'] == None:
        return redirect(url_for('login'))
    else:
        params = {
            "id": str(request.form['id'])
        }

        url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/delete_mongodb_product"
        response = requests.get(url, params)

        return render_template(
            'submitted_form.html',
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
