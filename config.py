import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Disable track modifications warning
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Connect to the database
# TODO IMPLEMENT DATABASE URL
# TODO IS DONE ^^^
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:asdf@localhost:5432/fyyur'
