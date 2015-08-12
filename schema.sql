drop table if exists persons;
drop table if exists pictures;
drop table if exists personsOnPicture;

create table persons (
    id integer primary key autoincrement,
    name text not null unique,
    session_key not null
    );

create table pictures (
    id integer primary key autoincrement,
    filename text not null unique,
    width integer not null,
    height integer not null,
    public_viewable integer not null
);

create table personsOnPicture (
    id integer primary key autoincrement,
    picture_id integer not null,
    person_id integer not null,
    FOREIGN KEY(picture_id) REFERENCES pictures(id),
    FOREIGN KEY(person_id) REFERENCES persons(id)
);
