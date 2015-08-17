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

@app.route("/tag/<string:person>/<string:picture_name>")
def tag_persons_pictures(person, picture_name):
    return tag_picture(picture_name, person)

@app.route("/tag/<string:picture_name>")
def tag_picture(picture_name, tag_person=None):
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
            prev, next = database.get_prev_and_next_picture_name(g.db, picture_name, tag_person)
            new_name = picture_name
            if request.args["action"] == "next":
                new_name = next
            if request.args["action"] == "prev":
                new_name = prev
            if new_name is None:
                if tag_person is not None:
                    return redirect("/private-pictures/"+str(tag_person))
                else:
                    return redirect("/tag")
            if tag_person is not None:
                return redirect("/tag/"+str(tag_person)+"/"+new_name)
            else:
                return redirect("/tag/"+new_name)

    stored_picture_data = database.get_picture_data(g.db, picture_name)
    persons_on_picture = map(lambda x: x["name"], database.get_all_persons_on_picture(g.db, picture_name))
    return render_template("tag.html",
                           picture_path = os.path.join("/pictures", picture_name),
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
    return render_template("private.html", pictures=pictures, person=person)

@app.route("/")
def main_view():
    return render_template("tag_main.html")

@app.route("/rename/<string:person>")
def rename_person(person):
    return rename(person)

@app.route("/rename")
def rename(selected_person=None):
    if len(request.args.viewkeys()) > 0:
        if "source_name" in request.args:
            source_name = request.args["source_name"]
        else:
            source_name = None
        if "new_name" in request.args:
            new_name = request.args["new_name"]
        else:
            new_name = None
        if "action" in request.args:
            if request.args["action"] == "rename":
                action = "rename"
            else:
                action = None
        else:
            action = None
        if source_name is not None and new_name is not None and action is not None:
            database.rename_person(g.db, source_name, new_name)
        return redirect("/rename")
    persons = map(lambda x: dict(name=x["name"], selected=x["name"]==selected_person), database.get_all_persons(g.db))
    return render_template("rename.html", persons=persons)

def reread_pictures(app):
    for filename in os.listdir(config.PICTURE_DIR):
        file_path = os.path.join(config.PICTURE_DIR, filename)
        im=Image.open(file_path)
        width, height = im.size
        db = database.connect_db(app)
        database.add_picture(db, filename, width, height, False)

def init_database(app):
    database.init_db(app)
    reread_pictures(app)

if __name__ == '__main__':
    app.run()