import json

def load_notes_from_json(fpath):
    """
    Load the notes from the json file
    """
    with open(fpath, "r") as infile:
        return [json.load(line) for line in infile] 