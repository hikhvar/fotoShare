__author__ = 'christoph'
# -*- coding: utf-8 -*-
import os

# configuration
DATABASE = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'fotoShare.db')
DEBUG = True
SECRET_KEY = os.urandom(2048)
USERNAME = 'admin'
PASSWORD = 'default'
PICTURE_DIR = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'pictures')
GREATER_TEXT = u"Unter dieser URL findet ihr eure persoenlichen Bilder von der Hochzeit: %s"
URL_PREFIX = "http://localhost:5000/"