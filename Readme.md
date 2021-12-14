# Project description

This project is a prototype furniture website which makes extensive use of cloud functionalities such as:

- Google Cloud Functions
- Firebase (For authentication)
- MongoDB (For most data storage)
- Google Cloud Store (For image data)

# Project layout

## app

The app folder contains the main Flask application that servers the web pages.

## cloudFunctions

This folder contains the source code for functions stored and used in Google Cloud Functions.

## databaseDetails

This folder contains information on the set up of the databases including starting sample data. Images have been left out in the interest of file size. All images stored in Google Cloud Storage are jpegs so you can access any image by going to:
'https://storage.googleapis.com/synthetic-cargo-products/619bb55c11dd33ac12d5aa0f.jpg'
The id can be swapped out for any id in Products.json -> imageId

## tests

This folder contains all the unit tests for this project. It makes use of the [unittest](https://docs.python.org/3/library/unittest.html) framework for Python.

# Tests

Each file tests a single other file. The test file is the name of the file being tested prefixed by "test\_". For example: main.py is tested in the test_main.py file.

Mocks have been used to fake the functionality of some function calls. Ideally everything outside of the file under test would be mocked but due to time constraints, only some key areas have been mocked including the Auth calls to Firebase and any write operations to the databases.

# Useful commands

To start the server (Ctrl + c to shutdown)

`python app/main.py`

To run the tests (from the root directory)

`python -m unittest discover -s tests`

# Troubleshooting import errors

Imports in a file under test don't always work well in Python, you may need to add the absolute path of the app folder into your Python set up folder:
Add a .pth file with the absolute path in it to here C:\Python39\Lib\site-packages
This helps unittest to discover the packages. The imports will work correctly as normal without this when starting the flask app.
