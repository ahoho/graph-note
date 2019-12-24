import json
import re
from datetime import datetime

from flask import Flask, render_template, request
from wtforms import Form, StringField

app = Flask(__name__)
notes = load_notes_json("notes.json")

def generate_links_from_text(text, tag='<p>'):
    """
    Parse the links to other entries
    """
    links


def save_form_as_json(form, fpath="notes.json"):
    clean_text, links = generate_links_from_text(form.text)
    form_dict = {
        "title": form.title.data,
        "subtitle": form.subtitle.data,
        "text": form.text.data,
        "links": generate_links_from_text(form.text),
    }
    # TODO: figure out best way to append to json file
    with open(fpath, "a") as outfile:
        json.dump(form_dict, outfile)
        outfile.write("\n")

def load_notes_json(fpath):
    """
    Load the notes from the json file
    """
    with open(fpath, "r") as infile:
         [json.load(line) for line in infile] 

@app.route("/create", methods=["GET", "POST"])
def create():
    """
    Create an entry
    """
    form = EntryForm(request.form)

    if request.method == "POST" and form.validate():
        save_form_as_json(form)
        return render_template("create.html", form=form)
       
    return render_template("create.html", form=form)


class EntryForm(Form):
    title = StringField('Title')
    subtitle = StringField('Subtitle')
    text = StringField('Text')
