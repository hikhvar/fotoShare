__author__ = 'christoph'
# -*- coding: utf-8 -*-
import os

_install_dir = os.path.split(os.path.realpath(__file__))[0]
# configuration
DATABASE = os.path.join(_install_dir, 'fotoShare.db')
DEBUG = True
SECRET_KEY = os.urandom(2048)
USERNAME = 'admin'
PASSWORD = 'default'
PICTURE_DIR = os.path.join(_install_dir, 'pictures')
GREATER_TEXT = u"Unter dieser URL findet ihr eure persoenlichen Bilder von der Hochzeit: %s"
URL_PREFIX = "http://petrausch.info/hochzeitsfotos/"