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

This folder contains information on the set up of the databases including starting sample data.

## tests

This folder contains all the unit tests for this project. It makes use of the [unittest](https://docs.python.org/3/library/unittest.html) framework for Python.

# Tests

Each file tests a single other file. The test file is the name of the file being tested prefixed by "test\_". For example: main.py is tested in the test_main.py file.

# Useful commands

To start the server (Ctrl + c to shutdown)

`python app/main.py`

To run the tests (from the root directory)

`python -m unittest discover -s tests`

# TODO

Add more unit tests (for main.py and tools.py)
PEP8 check
Comment functions
Update databaseDetails folder with current data
