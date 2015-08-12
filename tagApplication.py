__author__ = 'christoph'

# all the imports
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, send_file, send_from_directory, make_response
import sqlite3
from contextlib import closing
import database
import picture_viewing
import os.path
import os
import config
from PIL import Image
import csv
import collections
import StringIO

# create our little application :)
app = Flask(__name__)
app.config.from_object(config)

import shareApplication

@app.before_request
def before_request():
    g.db = database.connect_db(app)

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route("/tag")
def start_tagging():
    return render_template("tag_overview.html", pictures = database.get_all_picture_names(g.db))

@app.route("/tag/<string:picture_name>")
def tag_picture(picture_name):
    if len(request.args.viewkeys()) > 0:
        if "all" in request.args:
            database.alter_picture(g.db, picture_name, public=True)
        else:
            database.alter_picture(g.db, picture_name, public=False)
        if "persons" in request.args:
            old_persons = set(map(lambda x: x["name"], database.get_all_persons_on_picture(g.db, picture_name)))
            new_persons = set(filter(lambda x: len(x)>0, map(lambda x: x.strip(), request.args["persons"].splitlines())))
            added_persons = new_persons - old_persons
            deleted_persons = old_persons - new_persons
            for person in added_persons:
                database.add_person(g.db, person)
                database.connect_person_with_picture(g.db, picture_name, person)
            for person in deleted_persons:
                database.unconnect_person_from_picture(g.db, picture_name, person)
                if len(database.get_all_pictures_of_a_person(g.db, person)) < 1:
                    database.delete_person(g.db, person)
        if "action" in request.args:
            if request.args["action"] == "next":
                new_name = database.get_next_picture_name(g.db, picture_name)
                if new_name is None:
                    return redirect("/tag")
                return redirect("/tag/"+new_name)
    stored_picture_data = database.get_picture_data(g.db, picture_name)
    persons_on_picture = map(lambda x: x["name"], database.get_all_persons_on_picture(g.db, picture_name))
    return render_template("tag.html",
                           picture_path = os.path.join("..","pictures", picture_name),
                           picture_name = picture_name,
                           checked=stored_picture_data["public_viewable"],
                           persons = "\n".join(persons_on_picture)
                           )

@app.route("/pictures/<string:picture_name>")
def get_picture(picture_name):
    return send_from_directory(config.PICTURE_DIR, picture_name)

@app.route("/merge")
def merge():
    if len(request.args.viewkeys()) > 0:
        database.merge_session_keys(g.db, request.args)
    return render_template("merge.html", persons=database.get_all_persons(g.db))

@app.route("/export")
def export():
    all_persons = database.get_all_persons(g.db)
    sorted_dict = collections.defaultdict(list)
    for name, session_key in all_persons:
        sorted_dict[session_key].append(name)
    f = StringIO.StringIO()
    writer = csv.writer(f)
    for session_key, names in sorted_dict.iteritems():
        names_string = " ".join(names)
        url = config.URL_PREFIX + session_key
        writer.writerow([names_string, config.GREATER_TEXT % url])
    response = make_response(f.getvalue())
    # This is the key: Set the right header for the response
    # to be downloaded, instead of just printed on the browser
    response.headers["Content-Disposition"] = "attachment; filename=export.csv"
    return response

@app.route("/private-pictures/<string:person>")
def get_private_pictures(person):
    pictures = database.get_all_pictures_of_a_person(g.db, person)
    return render_template("private.html", pictures=pictures)

@app.route("/")
def main_view():
    return render_template("tag_main.html")


def reread_pictures(app):
    for filename in os.listdir(config.PICTURE_DIR):
        filepath = os.path.join(config.PICTURE_DIR, filename)
        im=Image.open(filepath)
        width, height = im.size
        db = database.connect_db(app)
        database.add_picture(db, filename, width, height, False)

def init_database(app):
    database.init_db(app)
    reread_pictures(app)

if __name__ == '__main__':
    app.run()