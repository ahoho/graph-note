import os
import re
import json

from note.models import Entry, Edge

def generate_links_from_text(text):
    """
    Parse the links to other entries,
    links are formatted as <id-name>
    """
    linked_ids = re.findall("(?<=<)[^<> ]+(?=>)", text)
    return linked_ids

    
def load_entries_from_json(fpath):
    """
    Load the notes from the json file
    """
    if not os.path.exists(fpath):
        return []
    with open(fpath, "r") as infile:
        return json.load(infile)

def entry_to_json(entry, edges=None):
    """
    Convert an entry to json
    """
    if edges is None:
        edges = Edge.query.filter(Edge.from_node == entry.id).all()
    
    entry_json = json.dumps({
        'id': entry.id,
        'title': entry.title,
        'text': entry.text,
        'links': [e.to_node for e in edges],
        'created_date': entry.created_date
    },indent="\t")
    return entry_json