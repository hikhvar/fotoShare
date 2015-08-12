__author__ = 'christoph'

# all the imports
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, send_file, send_from_directory
import sqlite3
from contextlib import closing
import database
import picture_viewing
import os.path
import config



# create our little application :)
app = Flask(__name__)
app.config.from_object(config)



@app.before_request
def before_request():
    g.db = database.connect_db(app)

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route("/<string:session_key>/<string:picture_name>")
def return_picture(session_key, picture_name):
    matching_pictures = database.get_pictures_with_session_key_and_name(g.db, session_key, picture_name)
    if len(matching_pictures) > 0:
        file_name = matching_pictures[0]["filename"]
        return send_from_directory(config.PICTURE_DIR, file_name)
    else:
        return "No Picture found"\

@app.route("/test")
def test_page():\
    return render_template("gallery.html")

@app.route("/all/<string:picture_name>")
def return_public_picture(picture_name):
    if database.is_picture_public(g.db, picture_name):
        return send_from_directory(config.PICTURE_DIR, picture_name)
    else:
        return "No Picture found"

@app.route("/<string:session_key>")
def return_gallery(session_key):
    pictures = database.get_all_pictures_of_a_session_key(g.db, session_key)
    public_pictures = database.get_all_public_pictures(g.db)
    if len(pictures) < 1:
        return "Sorry no pictures found. Maybe you inserted the wrong session key."
    else:
        #file_name = picture_viewing.create_zipfile(PICTURE_DIR, pictures)
        #return send_from_directory(*os.path.split(file_name), attachment_filename="pictures.zip", as_attachment=True)
        picture_list = picture_viewing.create_picture_list(pictures)
        return render_template("gallery.html",
                               session_key=session_key,
                               pictures=pictures,
                               public_pictures=public_pictures)

@app.route("/all")
def public_picture_gallery():
    public_pictures = database.get_all_public_pictures(g.db)
    return render_template("gallery.html", public_pictures=public_pictures)



if __name__ == '__main__':
    app.run()