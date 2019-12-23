import json

from flask import Flask, render_template, request
from wtforms import Form, StringField

app = Flask(__name__)

@app.route('/')
def index():
    return 'Index Page'

@app.route('/hello')
def hello():
    return 'Hello, World'

def save_form_as_json(form, fpath="notes.json"):
    form_dict = {
        "title": form.title.data,
        "subtitle": form.subtitle.data,
        "text": form.text.data,
        #"links": generate_links_from_text(form.text),
    }
    # TODO: figure out best way to append to json file
    with open(fpath, "a") as outfile:
        outfile.write("\n")
        json.dump(form_dict, outfile)

@app.route("/create", methods=["GET", "POST"])
def create():

    form = EntryForm(request.form)
    
    if request.method == "POST" and form.validate():
        save_form_as_json(form)
        return render_template("create.html", form=form)
       
    return render_template("create.html", form=form)


class EntryForm(Form):
    title = StringField('Title')
    subtitle = StringField('Subtitle')
    text = StringField('Text')
