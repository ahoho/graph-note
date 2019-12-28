import os
import json
import re
import pickle
import datetime

import markdown
from redis import Redis
from flask import Flask, render_template, request
from wtforms import Form, StringField

app = Flask(__name__)
# TODO: allow saving/loading with file rather than redis
# TODO: determine if redis is best tool for job, as opposed to SQL
# TODO: see what benefits there are from flask-redis
# TODO: what is best practice for saving/loading with Redis?
# TODO: profile to see if Redis is actually faster than disk
# TODO: make sure the redis flushing works
# TODO: consider making entries / entry classes 
# good Redis answer: https://stackoverflow.com/a/50504591/5712749
redis_client = Redis()
redis_client.flushdb()
redis_client.set("intialized", 0)

def generate_links_from_text(text):
    """
    Parse the links to other entries,
    links are formatted as <id-name>
    """
    linked_ids = re.findall("(?<=<)[^<> ]+(?=>)", text)
    # TODO: validate linked ids
    return linked_ids

def add_entry_to_redis(entry):
    """
    Store entry in redis, cleaning up its html
    """
    text = entry["text"]
    if isinstance(text, bytes):
        text = text.decode("utf-8")
    entry["links"] = ",".join(entry["links"])
    
    redis_client.lpush("entry_ids", entry["id"])
    redis_client.hmset(entry["id"], entry)

    text_html = re.sub("<([^<> ]+)>", "<a href=#\\1>\\1</a>", text)
    text_html = markdown.markdown(text_html)
    redis_client.hset(entry["id"], "text_html", text_html)

def save_entry_from_form(form, fpath="notes.json"):
    """
    Use the data created in the form to make a new entry
    """
    entry = {
        "id": form.title.data.replace(" ", "-").lower(),
        "title": form.title.data,
        "text": form.text.data,
        "links": generate_links_from_text(form.text.data),
        "created_date": (
            datetime.datetime
                    .now(tz=datetime.timezone.utc)
                    .astimezone()
                    .strftime('%Y-%m-%d %H:%M:%S %z')
        )
    }

    # save to json file
    with open(fpath, "a") as outfile:
        json.dump(entry, outfile)
        outfile.write("\n")

    # save to redis as well
    add_entry_to_redis(entry)

def load_entries_from_json(fpath):
    """
    Load the notes from the json file
    """
    if not os.path.exists(fpath):
        return []
    with open(fpath, "r") as infile:
        return [json.loads(line) for line in infile] 

@app.route("/")
def index():
    return "<a href=/create>create entry</a>"

@app.route("/create", methods=["GET", "POST"])
def create():
    """
    Create an entry
    """
    # first, load existing entries if not loaded
    if not redis_client.get("initialized") == b"1":
        redis_client.set("initialized", 1)
        data = load_entries_from_json("notes.json")
        for entry in data:
            add_entry_to_redis(entry)
    
    form = EntryForm(request.form)

    if request.method == "POST" and form.validate():
        save_entry_from_form(form)
        return render_template("create.html", form=form)
       
    return render_template("create.html", form=form)

@app.route("/notes")
def display_notes():
    """
    Show existing notes
    """
    entry_ids = redis_client.lrange("entry_ids", 0, -1)
    entries = []
    for id in entry_ids:
        entry = redis_client.hgetall(id)
        entry = {k.decode("utf-8"): v.decode("utf-8") for k, v in entry.items()}
        entries.append(entry)
    
    return render_template("notes.html", entries=entries)

class EntryForm(Form):
    title = StringField('Title')
    text = StringField('Text')
