__author__ = 'christoph'
import sqlite3
from flask import g
from contextlib import closing
import random
import string


def connect_db(app):
    conn =  sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def init_db(app):
    with closing(connect_db(app)) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def add_picture(db, picture_name, width, height, public):
    c = db.cursor()
    c.execute("SELECT * from pictures WHERE pictures.filename=?", (picture_name, ))
    if c.fetchone() is None:
        c.execute("INSERT INTO pictures (filename, width, height, public_viewable) VALUES (?, ?, ?, ?)", (picture_name, width, height, public))
        db.commit()
        return True
    else:
        return False

def alter_picture(db, picture_name, width=None, height=None, public=None):
    c = db.cursor()
    if width is not None:
        c.execute("UPDATE pictures SET width=? WHERE filename=? ", (width, picture_name))

    if height is not None:
        c.execute("UPDATE pictures SET height=? WHERE filename=? ", (height, picture_name))

    if public is not None:
        c.execute("UPDATE pictures SET public_viewable=? WHERE filename=? ", (public, picture_name))
    db.commit()

def add_person(db, person_name, session_key=None):
    if session_key is None:
        session_key = ''.join(random.choice(string.ascii_uppercase) for _ in range(6))
    c = db.cursor()
    c.execute("SELECT * from persons WHERE persons.name=?", (person_name, ))
    if c.fetchone() is None:
        c.execute("INSERT INTO persons (name, session_key) VALUES (?, ?)", (person_name, session_key))
        db.commit()
        return True
    else:
        return False

def delete_person(db, person_name):
    c = db.cursor()
    c.execute("DELETE FROM persons WHERE name=?", (person_name, ))
    db.commit()

def merge_session_keys(db, persons, session_key=None):
    if session_key is None:
        session_key = ''.join(random.choice(string.ascii_uppercase) for _ in range(6))
    c = db.cursor()
    for person in persons:
        c.execute("UPDATE persons SET session_key=? WHERE name=?", (session_key, person))
    db.commit()

def connect_person_with_picture(db, picture_name, person_name):
    c = db.cursor()
    c.execute("""
    INSERT
        INTO personsOnPicture (picture_id, person_id)
        VALUES
        (
         (SELECT id from pictures WHERE filename=?),
         (SELECT id from persons WHERE name=?)
        );
    """
    , (picture_name, person_name)
    )
    db.commit()

def unconnect_person_from_picture(db, picture_name, person_name):
    c = db.cursor()
    c.execute("""
    DELETE FROM personsOnPicture
     WHERE id IN (
        SELECT personsOnPicture.id
        FROM personsOnPicture
            INNER JOIN pictures ON personsOnPicture.picture_id=pictures.id
            INNER JOIN persons ON personsOnPicture.person_id=persons.id
        WHERE pictures.filename=?
        AND   persons.name=?
     )
    """
    , (picture_name, person_name)
    )
    db.commit()

def get_all_pictures_of_a_person(db, person_name):
    c = db.cursor()
    db_result = c.execute("""
    SELECT pictures.filename
    FROM personsOnPicture
        INNER JOIN pictures ON personsOnPicture.picture_id=pictures.id
        INNER JOIN persons ON personsOnPicture.person_id=persons.id
    WHERE
        persons.name=?;
    """
    , (person_name,)
    )
    return db_result.fetchall()

def get_all_pictures_of_a_session_key(db, session_key):
    c = db.cursor()
    db_result = c.execute("""
    SELECT pictures.filename, pictures.width, pictures.height
    FROM personsOnPicture
        INNER JOIN pictures ON personsOnPicture.picture_id=pictures.id
        INNER JOIN persons ON personsOnPicture.person_id=persons.id
    WHERE
        persons.session_key=?;
    """
    , (session_key,)
    )
    return db_result.fetchall()

def get_pictures_with_session_key_and_name(db, session_key, picture_name):
    c = db.cursor()
    db_result = c.execute("""
    SELECT pictures.filename
    FROM personsOnPicture
        INNER JOIN pictures ON personsOnPicture.picture_id=pictures.id
        INNER JOIN persons ON personsOnPicture.person_id=persons.id
    WHERE
        persons.session_key=?
    AND
        pictures.filename=?;
    """
    , (session_key, picture_name)
    )
    return db_result.fetchall()

def get_picture_data(db, picture_name):
    c = db.cursor()
    db_result = c.execute("""
    SELECT *
    FROM pictures
    WHERE
        pictures.filename=?;
    """
    , ( picture_name, )
    )
    return db_result.fetchone()

def get_all_persons_on_picture(db, picture_name):
    c = db.cursor()
    db_result = c.execute("""
    SELECT persons.name
    FROM personsOnPicture
        INNER JOIN pictures ON personsOnPicture.picture_id=pictures.id
        INNER JOIN persons ON personsOnPicture.person_id=persons.id
    WHERE
        pictures.filename=?;
    """
    , ( picture_name, )
    )
    return db_result.fetchall()

def get_next_picture_name(db, picture_name):
    c = db.cursor()
    db_result = c.execute("""
    SELECT filename
    FROM pictures
    ORDER BY filename;
    """)
    while db_result.fetchone()["filename"] != picture_name:
        pass
    row =  db_result.fetchone()
    if row is None:
        return None
    else:
        return row["filename"]

def get_all_picture_names(db):
    c = db.cursor()
    return map(lambda x: x["filename"],
               c.execute("""
               SELECT filename from pictures ORDER BY filename;"""))

def is_picture_public(db, picture_name):
    c = db.cursor()
    result = c.execute("""
    SELECT *
    FROM pictures
    WHERE
        filename=?
    AND
        public_viewable=1""", (picture_name, ))
    return result.fetchone() is not None

def get_all_public_pictures(db):
    c = db.cursor()
    result = c.execute("""
    SELECT *
    FROM pictures
    WHERE public_viewable=1
    ORDER BY filename""")
    return result.fetchall()

def get_all_persons(db):
    c = db.cursor()
    return c.execute("""
    SELECT name, session_key
    FROM persons
    ORDER BY session_key;
    """)


