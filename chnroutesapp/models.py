from google.appengine.ext import db


class MyFile(db.Model):
    name = db.StringProperty(required=True)
    blob_key = db.StringProperty(required=True)
    update_date = db.DateProperty()