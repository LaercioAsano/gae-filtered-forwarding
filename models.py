from google.appengine.ext import ndb

class Email(ndb.Model):
    """Sub model for representing an email."""
    sender = ndb.StringProperty(indexed=False)
    subject = ndb.StringProperty(indexed=False)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(indexed=True)

    @classmethod
    def get_root(cls):
        return ndb.Key("Email", "root")

class Subscriber(ndb.Model):
    """Sub model for representing a subscriber."""
    uid = ndb.StringProperty(indexed=True)
    name = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty()
    words = ndb.StringProperty(indexed=False, repeated=True)
    forwarded = ndb.StructuredProperty(Email, indexed=False, repeated=True)

    @classmethod
    def get_root(cls):
        return ndb.Key("Subscriber", "root")
