import base64
import logging
import requests
import json
from flask import Flask, render_template, request, url_for, redirect
import tools
import uuid

app = Flask(__name__)


@app.route('/')
@app.route('/home')
def home():
    url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/read_mongodb_products"
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


@app.route('/update_product')
def update_product():
    authContent = tools.authenticateUser(request.cookies.get("token"))

    # If not authenticated
    if authContent['user_data'] == None:
        return redirect(url_for('login'))
    else:
        product_id = request.args.get('id')

        # Get product text data
        url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/read_mongodb_products"
        response = requests.get(url, {'id': product_id})
        product_info = json.loads(response.content.decode("utf-8"))

        # Change the tag list into a string for formatting
        formattedTags = ""
        for tag in product_info['tags']:
            formattedTags += tag + ","
        formattedTags = formattedTags[0:-1]
        product_info['tags'] = formattedTags.lower()

        return render_template('update_product.html',
                               product_info=product_info,
                               user_data=authContent['user_data'])


@app.route('/admin')
def form():
    authContent = tools.authenticateUser(request.cookies.get("token"))

    # If not authenticated
    if authContent['user_data'] == None:
        return redirect(url_for('login'))
    else:

        # TODO Update delete function to show summary of products

        # Get product text data
        url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/read_mongodb_products"
        response = requests.get(url)
        product_info = json.loads(response.content.decode("utf-8"))

        # Get product image names
        url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/cloud-storage-product-get"
        product_images = requests.get(url)
        product_images = json.loads(product_images.content.decode("utf-8"))

        return render_template('admin.html',
                               product_info=product_info,
                               product_images=product_images,
                               user_data=authContent['user_data'])


@app.route('/create_product_submitted', methods=['POST'])
def create_product_submitted_form():
    authContent = tools.authenticateUser(request.cookies.get("token"))

    # If not authenticated
    if authContent['user_data'] == None:
        return redirect(url_for('login'))
    else:

        imageID = str(uuid.uuid4())

        # Create the product text in MongoDB
        params = {
            "title": str(request.form['title']),
            "description": str(request.form['description']),
            "pricePerUnit": str(request.form['pricePerUnit']),
            "qty": int(request.form['qty']),
            "imageID": imageID,
            "tags": request.form['tags'].split(",")
        }
        mongoUrl = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/create_mongodb_product"
        # TODO Change this and related Google function to use post not get
        mongoResponse = requests.get(mongoUrl, params)

        # Upload the image to Google Cloud Storage
        base64Image = base64.b64encode(request.files['image'].read())
        googleUrl = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/upload_cloud_storage_image"
        googleParams = {
            "id": imageID,
            "image": base64Image
        }
        googleResponse = requests.post(
            googleUrl, googleParams)

        return render_template(
            'submitted_form.html',
            title=params['title'],
            description=params['description'],
            pricePerUnit=params['pricePerUnit'],
            qty=params['qty'],
            imageID=params['imageID'],
            tags=params['tags'],
            user_data=authContent['user_data'],
            error_message=authContent['error_message'],
            response="Successfully added to databases!"
        )


@app.route('/update_product_submitted', methods=['POST'])
def update_product_submitted():
    authContent = tools.authenticateUser(request.cookies.get("token"))

    # If not authenticated
    if authContent['user_data'] == None:
        return redirect(url_for('login'))
    else:
        serverResponse = ""

        # Get product imageID data
        url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/read_mongodb_products"
        response = requests.get(url, {'id': request.form['id']})
        oldImageID = json.loads(response.content.decode("utf-8"))['imageID']

        newImageID = str(uuid.uuid4())

        # Update MongoDB
        params = {
            "id": str(request.form['id']),
            "title": str(request.form['title']),
            "description": str(request.form['description']),
            "pricePerUnit": str(request.form['pricePerUnit']),
            "qty": int(request.form['qty']),
            "imageID": newImageID,
            "tags": request.form['tags'].split(",")
        }
        url = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/update_mongodb_product"
        response = requests.get(url, params)

        serverResponse += "Text Updated"

        # Update image in cloud storage
        if request.files['image'].filename == '':
            serverResponse += " and image not updated"
        else:
            # Add new image
            base64Image = base64.b64encode(request.files['image'].read())
            googleUrl = "https://europe-west2-synthetic-cargo-328708.cloudfunctions.net/upload_cloud_storage_image"
            googleParams = {
                "id": newImageID,
                "image": base64Image
            }
            googleResponse = requests.post(
                googleUrl, googleParams)

            # Remove old image
            print("Remove old image")
            # TODO Remove old image

            serverResponse += " and image updated"

        # TODO Make function to turn tags list into string
        return render_template(
            'submitted_form.html',
            title=params['title'],
            description=params['description'],
            pricePerUnit=params['pricePerUnit'],
            qty=params['qty'],
            tags=params['tags'],
            user_data=authContent['user_data'],
            error_message=authContent['error_message'],
            response=serverResponse
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

        # TODO Make delete html page
        return render_template(
            'submitted_form.html',
            user_data=authContent['user_data'],
            error_message=authContent['error_message'],
            response=response.content.decode("utf-8")
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
