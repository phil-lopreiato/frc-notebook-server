import logging

from google.appengine.ext import ndb
from google.appengine.api import users

from models.mobile_user import MobileUser


class PushHelper(object):

    @classmethod
    def user_email_to_id(cls, user_email):
        '''
        Returns the user id for a given email address (or None if invalid)
        workaround for this bug: https://code.google.com/p/googleappengine/issues/detail?id=8848
        solution from: http://stackoverflow.com/questions/816372/how-can-i-determine-a-user-id-based-on-an-email-address-in-app-engine
        '''
        u = users.User(user_email)
        key = MobileUser(user=u).put()
        obj = key.get()
        user_id = obj.user.user_id()
        key.delete()
        return user_id

    @classmethod
    def delete_bad_gcm_token(cls, key):
        logging.info("removing bad GCM token: {}".format(key))
        to_delete = MobileClient.query(MobileClient.messaging_id == key).fetch(keys_only=True)
        ndb.delete_multi(to_delete)

    @classmethod
    def update_token(cls, old, new):
        to_update = MobileClient.query(MobileClient.messaging_id == old).fetch()
        for model in to_update:
            model.messaging_id = new
            model.put()
