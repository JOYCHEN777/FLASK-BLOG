import os


class Config(object):
    SECRET_KEY = 'da43bc5f4d53dd8903a3b4bf972ed09f8e244e44e0b27d92'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://database_information'
    SQLALCHEMY_TRACK_MODIFICATION = False