from google.appengine.ext import ndb


class Collaberator(ndb.Model):
    """
    Represents collab relationship at events
    Notifications will only be sent if both the
    sender and receiver have shared with each other
    """

    srcUserId = ndb.IntegerProperty(required=True)
    dstUserId = ndb.IntegerProperty(required=True)
    mutual = ndb.BooleanProperty(default=False)
    eventKey = ndb.StringProperty(reqiored=True)

    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True, indexed=False)
