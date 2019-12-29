import re
import datetime

import markdown
from sqlalchemy import Column, Integer, String, UnicodeText
from wtforms import Form, StringField

from note.database import Base

class Entry(Base):
    __tablename__ = 'entries'
    id = Column(String(100), primary_key=True)
    title = Column(String(100), unique=False)
    text = Column(UnicodeText, unique=False)
    text_html = Column(UnicodeText, unique=False)
    created_date = Column(String(40), unique=False)

    def __init__(self, title, text, created_date=None):
        self.id = title.replace(" ", "-").lower()
        self.title = title
        self.text = text
        self.created_date = created_date
        if created_date is None:
            self.created_date =  (
                datetime.datetime
                        .now(tz=datetime.timezone.utc)
                        .astimezone()
                        .strftime('%Y-%m-%d %H:%M:%S %z')
            )
        self.text_html = self.convert_text_to_html(text)

    @staticmethod
    def convert_text_to_html(text):
        """
        Convert markdown to html
        """
        text_html = re.sub("<([^<> ]+)>", "<a href=#\\1>\\1</a>", text)
        text_html = markdown.markdown(text_html)
        return text_html

    def __repr__(self):
        return f"<Entry {self.id}>"

class EntryForm(Form):
    title = StringField('Title') #TODO: limit to 100
    text = StringField('Text')

class Edge(Base):
    __tablename__ = 'edges'
    edge_id = Column(Integer(), primary_key=True)
    from_node = Column(String(100), unique=False)
    to_node = Column(String(100), unique=False)

    def __init__(self, from_node, to_node):
        self.from_node = from_node
        self.to_node = to_node

    def __repr__(self):
        return f"<Link from {self.from_node} to {self.to_node}>"