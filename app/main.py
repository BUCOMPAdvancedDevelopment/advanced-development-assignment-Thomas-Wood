import base64
from datetime import datetime, timedelta
import logging
import json
from flask import Flask, render_template, request, url_for, redirect
import tools
import uuid

app = Flask(__name__)


@app.route('/')
@app.route('/home', methods=['GET'])
def home():
    """The main landing page of the site.
    It contains a list of all the products available, each with an 'Add to basket' button.
    If you're an Admin, you also have a 'edit' button to edit the product.
    Account: Not required
    Admin: Not required
    """
    authContent = tools.authenticateUser(request.cookies.get("token"))

    product_info = tools.formatProductData(
        tools.getProduct())

    return render_template('home.html',
                           product_info=product_info,
                           user_data=authContent['user_data'])


@app.route('/about', methods=['GET'])
def about():
    """The about page which contains some simple contact details
    Account: Not required
    Admin: Not required
    """
    authContent = tools.authenticateUser(request.cookies.get("token"))

    return render_template('about.html',
                           user_data=authContent['user_data'])


@app.route('/login', methods=['GET'])
def login():
    """The login page for the site.
    It uses firebase to authenticate the user (Google accounts only)
    On the first login, a document in the database will be created for the user
    Account: Not required
    Admin: Not required
    """
    authContent = tools.authenticateUser(request.cookies.get("token"))

    return render_template(
        'login.html',
        user_data=authContent['user_data'],
        error_message=authContent['error_message'])


@app.route('/basket', methods=['GET'])
def basket():
    """This shows the items currently in the user's basket
    Products can be removed from the basket
    Account: Required
    Admin: Not required
    """
    authContent = tools.authenticateUser(request.cookies.get("token"))

    # If not authenticated
    if authContent['user_data'] == None:
        return redirect(url_for('login'))
    else:
        # Add some details to the products
        runningTotal = 0
        for item in authContent['user_data']['basket']:
            product = tools.getProduct(item['productId'])
            item['title'] = product['title']
            item['imageID'] = product['imageID']
            item['pricePerUnit'] = float(product['pricePerUnit'])
            item['qty'] = int(item['qty'])
            runningTotal += item['pricePerUnit']*item['qty']

        return render_template('basket.html',
                               user_data=authContent['user_data'],
                               totalPrice=runningTotal)


@app.route('/add_to_basket', methods=['POST'])
def addToBasket():
    """A background post call to add a product to the user's basket.
    Account: Required
    Admin: Not required
    """
    authContent = tools.authenticateUser(request.cookies.get("token"))

    # If not authenticated
    if authContent['user_data'] == None:
        return redirect(url_for('login'))
    else:
        userId = authContent['user_data']['userId']
        productId = request.form['id']
        qty = request.form['qty']

        response = tools.addToBasket(userId, productId, qty)

        if response == 201:
            return "Success", 201
        else:
            return "Something went wrong", 500


@app.route('/remove_from_basket', methods=['POST'])
def removeFromBasket():
    """This removes a product from the basket and redirects the user back to their basket
    Account: Required
    Admin: Not required
    """
    authContent = tools.authenticateUser(request.cookies.get("token"))

    # If not authenticated
    if authContent['user_data'] == None:
        return redirect(url_for('login'))
    else:
        userId = authContent['user_data']['userId']
        basketIndex = request.form['basketIndex']

        response = tools.removeFromBasket(userId, basketIndex)

        if response == 201:
            return redirect(url_for('basket'))
        else:
            return render_template('message.html',
                                   message_title='Something went wrong',
                                   message_body="We're not sure what went wrong, but we're looking into it. Try again in a few mins",
                                   user_data=authContent['user_data']), 500


@app.route('/orders', methods=['GET'])
def viewOrders():
    """This shows all orders an account has made
    Account: Required
    Admin: Not required
    """
    authContent = tools.authenticateUser(request.cookies.get("token"))

    # If not authenticated
    if authContent['user_data'] == None:
        return redirect(url_for('login'))
    else:
        return render_template('orders.html',
                               user_data=authContent['user_data'])


@app.route('/create_order', methods=['GET'])
def createOrder():
    """This page is where the user fills in their address for the order
    Account: Required
    Admin: Not required
    """
    authContent = tools.authenticateUser(request.cookies.get("token"))

    # If not authenticated
    if authContent['user_data'] == None:
        return redirect(url_for('login'))
    else:
        return render_template('create_order.html',
                               user_data=authContent['user_data'])


@app.route('/create_order', methods=['POST'])
def submitOrder():
    """This creates an order from the user's basket then redirects them to their order
    Account: Required
    Admin: Not required
    """
    authContent = tools.authenticateUser(request.cookies.get("token"))

    # If not authenticated
    if authContent['user_data'] == None:
        return redirect(url_for('login'))
    else:
        runningTotal = 0
        for item in authContent['user_data']['basket']:
            product = tools.getProduct(item['productId'])
            runningTotal += float(product['pricePerUnit'])*int(item['qty'])

        orderDetails = {
            'userId': authContent['user_data']['userId'],
            'timestamp': str(datetime.now()),
            'name': request.form['name'],
            'address': request.form['address'],
            'paymentType': request.form['paymentType'],
            'content': json.dumps(authContent['user_data']['basket']),
            'expectedDeliveryDate': str(datetime.now() + timedelta(days=7)),
            'totalCost': runningTotal,
            'status': 'Preparing'
        }

        # Send to google function to create order and empty basket
        response = tools.createOrder(orderDetails)

        if response == 201:
            return redirect(url_for('viewOrders'))
        else:
            return render_template('message.html',
                                   message_title='Something went wrong',
                                   message_body="We're not sure what went wrong, but we're looking into it. Try again in a few mins",
                                   user_data=authContent['user_data']), 500


@app.route('/update_product', methods=['GET'])
def update_product():
    """A page to edit details about an existing product. Only accessible by admins
    Account: Required
    Admin: Required
    """
    authContent = tools.authenticateUser(request.cookies.get("token"))

    # If not authenticated
    if authContent['user_data'] == None:
        return redirect(url_for('login'))
    elif authContent['user_data']['admin'] == False:
        return unauthorised(authContent)
    else:
        product_id = request.args.get('id')

        product_info = tools.getProduct(product_id)

        # Change the tag list into a string for formatting
        formattedTags = ""
        for tag in product_info['tags']:
            formattedTags += tag + ","
        formattedTags = formattedTags[0:-1]
        product_info['tags'] = formattedTags.lower()

        return render_template('update_product.html',
                               product_info=product_info,
                               user_data=authContent['user_data'])


@app.route('/admin', methods=['GET'])
def admin():
    """The main admin page.
    Has functionality to create and delete products and view, edit and delete users (and their order status)
    Account: Required
    Admin: Required
    """
    authContent = tools.authenticateUser(request.cookies.get("token"))

    # If not authenticated
    if authContent['user_data'] == None:
        return redirect(url_for('login'))
    elif authContent['user_data']['admin'] == False:
        return unauthorised(authContent)
    else:
        product_info = tools.getProduct()
        customer_data = tools.getUserSummaries()

        return render_template('admin.html',
                               product_info=product_info,
                               customer_data=customer_data,
                               user_data=authContent['user_data'])


@app.route('/edit_user', methods=['GET'])
def edit_user():
    """A page to edit details in a user account (and their orders)
    Account: Required
    Admin: Required
    """
    authContent = tools.authenticateUser(request.cookies.get("token"))

    # If not authenticated
    if authContent['user_data'] == None:
        return redirect(url_for('login'))
    elif authContent['user_data']['admin'] == False:
        return unauthorised(authContent)
    else:
        customer_id = request.args.get('id')
        customer_data = tools.getUserData(customer_id)
        return render_template('edit_user_details.html',
                               customer_data=customer_data,
                               user_data=authContent['user_data'])


@app.route('/delete_user', methods=['GET'])
def delete_user():
    """This deletes a user and redirects the admin to a confirmation page
    Account: Required
    Admin: Required
    """
    authContent = tools.authenticateUser(request.cookies.get("token"))

    # If not authenticated
    if authContent['user_data'] == None:
        return redirect(url_for('login'))
    elif authContent['user_data']['admin'] == False:
        return unauthorised(authContent)
    else:
        response = tools.deleteUser(request.args.get('id'))

        if response == 200:
            return render_template('message.html',
                                   message_title='User Deleted',
                                   message_body='The user account has been deleted',
                                   user_data=authContent['user_data'])
        else:
            return render_template('message.html',
                                   message_title='Something went wrong',
                                   message_body="We're looking into the problem, try again in a few mins",
                                   user_data=authContent['user_data'])


@app.route('/update_user_submitted', methods=['POST'])
def update_user():
    """This updates a user's details then redirects the admin to a confirmation page
    Account: Required
    Admin: Required
    """
    authContent = tools.authenticateUser(request.cookies.get("token"))

    # If not authenticated
    if authContent['user_data'] == None:
        return redirect(url_for('login'))
    elif authContent['user_data']['admin'] == False:
        return unauthorised(authContent)
    else:
        if request.form['admin'] == 'on':
            admin = True
        else:
            admin = False

        orderStatuses = []
        for key in request.form.keys():
            if "orderStatusIndex" in key:
                orderStatuses.append(request.form[key])

        params = {
            'userId': request.form['userId'],
            'name': request.form['name'],
            'admin': admin,
            'orderStatuses': json.dumps(orderStatuses)
        }

        response = tools.updateUser(params)

        if response == 200:
            return render_template('message.html',
                                   message_title='User Updated',
                                   message_body='The user account has been updated',
                                   user_data=authContent['user_data'])
        else:
            return render_template('message.html',
                                   message_title='Something went wrong',
                                   message_body="We're looking into the problem, try again in a few mins",
                                   user_data=authContent['user_data'])


@app.route('/update_personal_details', methods=['GET'])
def view_personal_details():
    """This shows a user their details and allows them to edit some parts
    Account: Required
    Admin: Not required
    """
    authContent = tools.authenticateUser(request.cookies.get("token"))

    # If not authenticated
    if authContent['user_data'] == None:
        return redirect(url_for('login'))
    else:
        return render_template('edit_personal_details.html',
                               user_data=authContent['user_data'])


@app.route('/update_personal_details_submitted', methods=['POST'])
def update_personal_details():
    """This updates a user's own details
    Account: Required
    Admin: Not required
    """
    authContent = tools.authenticateUser(request.cookies.get("token"))

    # If not authenticated
    if authContent['user_data'] == None:
        return redirect(url_for('login'))
    else:
        admin = authContent['user_data']['admin']

        orderStatuses = []
        for key in request.form.keys():
            if "orderStatusIndex" in key:
                orderStatuses.append(request.form[key])

        params = {
            'userId': request.form['userId'],
            'name': request.form['name'],
            'admin': admin,
            'orderStatuses': json.dumps(orderStatuses)
        }

        response = tools.updateUser(params)

        if response == 200:
            return render_template('message.html',
                                   message_title='Details Updated',
                                   message_body='Your account has been updated',
                                   user_data=authContent['user_data'])
        else:
            return render_template('message.html',
                                   message_title='Something went wrong',
                                   message_body="We're looking into the problem, try again in a few mins",
                                   user_data=authContent['user_data'])


@app.route('/create_product_submitted', methods=['POST'])
def create_product_submitted_form():
    """This creates a new product then redirects the admin to a confirmation page
    Account: Required
    Admin: Required
    """
    authContent = tools.authenticateUser(request.cookies.get("token"))

    # If not authenticated
    if authContent['user_data'] == None:
        return redirect(url_for('login'))
    elif authContent['user_data']['admin'] == False:
        return unauthorised(authContent)
    else:

        imageID = str(uuid.uuid4())

        # Create the product text in MongoDB
        params = {
            "title": str(request.form['title']),
            "description": str(request.form['description']),
            "pricePerUnit": str(request.form['pricePerUnit']),
            "qty": int(request.form['qty']),
            "imageID": imageID,
            "tags": request.form['tags']
        }
        mongoResponse = tools.createProduct(params)

        # Upload the image to Google Cloud Storage
        base64Image = base64.b64encode(request.files['image'].read())
        googleResponse = tools.uploadImage(imageID, base64Image)

        if mongoResponse == 200 and googleResponse == 200:
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
        else:
            return render_template('message.html',
                                   message_title='Something went wrong',
                                   message_body="We're looking into the problem, try again in a few mins",
                                   user_data=authContent['user_data'])


@app.route('/update_product_submitted', methods=['POST'])
def update_product_submitted():
    """This updates details about an existing product. Only accessible by admins
    Account: Required
    Admin: Required
    """
    authContent = tools.authenticateUser(request.cookies.get("token"))

    # If not authenticated
    if authContent['user_data'] == None:
        return redirect(url_for('login'))
    elif authContent['user_data']['admin'] == False:
        return unauthorised(authContent)
    else:
        # Get product imageID data
        oldImageID = tools.getProduct(request.form['id'])['imageID']
        newImageID = str(uuid.uuid4())

        googleUploadResponse = None
        googleRemoveResponse = None

        # Update MongoDB
        params = {
            "id": str(request.form['id']),
            "title": str(request.form['title']),
            "description": str(request.form['description']),
            "pricePerUnit": str(request.form['pricePerUnit']),
            "qty": int(request.form['qty']),
            "imageID": newImageID,
            "tags": request.form['tags']
        }
        mongoResponse = tools.updateProduct(params)

        # Update image in cloud storage if one was uploaded
        if request.files['image'].filename != '':

            # Upload new image
            base64Image = base64.b64encode(request.files['image'].read())
            googleUploadResponse = tools.uploadImage(newImageID, base64Image)

            # Remove old image
            googleRemoveResponse = tools.deleteImage(oldImageID)

        if (mongoResponse == 200 and
                (googleUploadResponse == 200 or googleUploadResponse == None) and
                (googleRemoveResponse == 200 or googleRemoveResponse == None)):
            return render_template('message.html',
                                   message_title='Product updated',
                                   message_body='The product details have been updated',
                                   user_data=authContent['user_data'])
        else:
            return render_template('message.html',
                                   message_title='Something went wrong',
                                   message_body="We're looking into the problem, try again in a few mins",
                                   user_data=authContent['user_data'])


@app.route('/delete_product_submitted', methods=['POST'])
def delete_product_submitted_form():
    """This deletes an existing product. Only accessible by admins
    Account: Required
    Admin: Required
    """
    authContent = tools.authenticateUser(request.cookies.get("token"))

    # If not authenticated
    if authContent['user_data'] == None:
        return redirect(url_for('login'))
    elif authContent['user_data']['admin'] == False:
        return unauthorised(authContent)
    else:
        # Get product imageID data
        imageID = tools.getProduct(request.form['id'])['imageID']

        # Remove Mongo object
        mongoResponse = tools.deleteProduct(request.form['id'])

        # Remove image
        googleResponse = tools.deleteImage(imageID)

        if mongoResponse == 200 and googleResponse == 200:
            return render_template('message.html',
                                   message_title='Product Deleted',
                                   message_body='The product has been deleted',
                                   user_data=authContent['user_data'])
        else:
            return render_template('message.html',
                                   message_title='Something went wrong',
                                   message_body="We're looking into the problem, try again in a few mins",
                                   user_data=authContent['user_data'])


@app.errorhandler(500)
def server_error(error):
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


def unauthorised(authContent):
    render_template('message.html',
                    message_title='Unauthorised',
                    message_body='Your account does not have the permissions required to access this page',
                    user_data=authContent['user_data']), 403


if __name__ == '__main__':
    # Only run for local development.
    app.run(host='127.0.0.1', port=8080, debug=True)
