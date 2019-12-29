import json
import datetime

import markdown
from flask import render_template, request

from note import app
from note.models import Entry, Edge, EntryForm
from note.utils import generate_links_from_text, load_entries_from_json, entry_to_json
import note.database as db

@app.route("/")
def index():    
    return "<a href=/create>create entry</a>"

@app.route("/refresh")
def gen_db_from_json():
    """
    Create the database from json
    """
    # delete tables from the old database and reinitialize the tables
    json_entries = load_entries_from_json("notes.json")
    if json_entries:
        db.delete_tables()
    else:
        # TODO: warn with logging module
        print("notes.json is empty, so no tables deleted")

    db.init_db()

    # add entries
    entries = [
        Entry(entry["title"], entry["text"], entry["created_date"])
        for entry in json_entries
    ]
    db.db_session.bulk_save_objects(entries)

    # add edges
    edges = [
        Edge(entry["id"], node_id)
        for entry in json_entries
        for node_id in entry["links"]
    ]
    db.db_session.bulk_save_objects(edges)

    db.db_session.commit()

    return f"Database successfully refreshed with {len(entries)} entries"

@app.route("/save")
def save_db_as_json():
    """
    Save the database to json
    """
    entries = Entry.query.all()

    with open("notes.json", "w") as outfile:
        for i, entry in enumerate(entries):
            entry_json = entry_to_json(entry)
            outfile.write(entry_json)
            if i < (len(entries) - 1):
                outfile.write("\n")

    return f"Saved {len(entries)} entries to notes.json"


@app.route("/create", methods=["GET", "POST"])
def create():
    """
    Create an entry
    """    
    form = EntryForm(request.form)

    if request.method == "POST" and form.validate():
        # create entries
        entry = Entry(form.data["title"], form.data["text"])
        db.db_session.add(entry)

        # create edges
        linked_ids = generate_links_from_text(form.data["text"])
        # TODO: make sure links refer to existing edges
        edges = [Edge(entry.id, id) for id in linked_ids]
        db.db_session.bulk_save_objects(edges)

        # commit to database
        try:
            db.db_session.commit()
        except db.IntegrityError as e:
            return f"Title {form.data['title']} is not unique"

        with open("notes.json", "a") as outfile:
            entry_json = entry_to_json(entry, edges=linked_ids)
            outfile.write("\n")
            outfile.write(entry_json)
        
        # TODO: go to this entry in the results
        return render_template("create.html", form=form)
       
    return render_template("create.html", form=form)

@app.route("/notes")
def display_notes():
    """
    Show existing notes
    """
    entries = Entry.query.all()
    return render_template("notes.html", entries=entries)