import ConfigParser
import endpoints
import os
import logging

from google.appengine.ext import ndb
from protorpc import remote
from protorpc import message_types

from models.mobile_messages import RegistrationRequest, NoteMessage, BaseResponse, NoteResponse, NoteListResponse, CollaboratorAdd, CollaboratorRemove
from consts.client_type import ClientType
from helpers.push_helper import PushHelper
from models.mobile_client import MobileClient
from models.collaborator import Collaborator

config = ConfigParser.ConfigParser()
config.readfp(open('config.ini'))

client_id_sitevar = config.get('endpoints', 'webId')
logging.info("WebID: {}".format(client_id_sitevar))
if client_id_sitevar is None:
    raise Exception("Sitevar appengine.webClientId is undefined. Can't process incoming requests")
WEB_CLIENT_ID = str(client_id_sitevar)
ANDROID_AUDIENCE = WEB_CLIENT_ID

android_id_sitevar = config.get('endpoints', 'androidId')
if android_id_sitevar is None:
    raise Exception("Sitevar android.clientId is undefined. Can't process incoming requests")
ANDROID_CLIENT_ID = str(android_id_sitevar)

# To enable iOS access to the API, add another variable for the iOS client ID

client_ids = [WEB_CLIENT_ID, ANDROID_CLIENT_ID]
# TODO this
'''
Only allow API Explorer access on dev versions
'''
# client_ids.append(endpoints.API_EXPLORER_CLIENT_ID)


@endpoints.api(name='frcNotebookMobile', version='v1', description="API for FRC Notebook",
               allowed_client_ids=client_ids,
               audiences=[ANDROID_AUDIENCE],
               scopes=[endpoints.EMAIL_SCOPE])
class MobileAPI(remote.Service):

    @endpoints.method(RegistrationRequest, BaseResponse,
                      path='register', http_method='POST',
                      name='register')
    def register_client(self, request):
        current_user = endpoints.get_current_user()
        if current_user is None:
            return BaseResponse(code=401, data="Unauthorized to register")
        userId = PushHelper.user_email_to_id(current_user.email())
        gcmId = request.mobile_id
        os = ClientType.enums[request.operating_system]
        name = request.name
        uuid = request.device_uuid

        query = MobileClient.query(MobileClient.user_id == userId, MobileClient.device_uuid == uuid, MobileClient.client_type == os)
        # trying to figure out an elusive dupe bug
        logging.info("DEBUGGING")
        logging.info("User ID: {}".format(userId))
        logging.info("UUID: {}".format(uuid))
        logging.info("Count: {}".format(query.count()))
        if query.count() == 0:
            # Record doesn't exist yet, so add it
            MobileClient(
                user_id=userId,
                messaging_id=gcmId,
                client_type=os,
                device_uuid=uuid,
                display_name=name).put()
            return BaseResponse(code=200, data="Registration successful")
        else:
            # Record already exists, update it
            client = query.fetch(1)[0]
            client.messaging_id = gcmId
            client.display_name = name
            client.put()
            return BaseResponse(code=304, data="Client already exists")

    @endpoints.method(CollaboratorAdd, BaseResponse,
                      path='/collaborator/add', http_method='POST',
                      name='collaboratorAdd')
    def collaborator_add(self, request):
        current_user = endpoints.get_current_user()
        if current_user is None:
            return BaseResponse(code=401, data="Unauthorized to add collaborators")
        if current_user.email() == request.email:
            return BaseResponse(code=500, data="Can't collaborate with yourself")
        user_id = PushHelper.user_email_to_id(current_user.email())
        new_user_id = PushHelper.user_email_to_id(request.email)

        # See if this combination has been added before
        result = Collaborator.query((Collaborator.srcUserId == user_id and Collaborator.dstUserId == new_user_id and Collaborator.eventKey == request.eventKey) or (Collaborator.srcUserId == new_user_id and Collaborator.dstUserId == user_id and Collaborator.eventKey == request.eventKey)).fetch(limit=1)

        if result is not None and len(result) > 0:
            existing = result[0]
            if existing.mutual:
                # This relationship already exists
                return BaseResponse(code=304, data="This collaboration already exists")
            elif existing.dstUserId == user_id and existing.srcUserId == new_user_id:
                # If this has been added the other way, mark as mutual
                existing.mutual = True
                existing.put()
                return BaseResponse(code=200, data="Collaboration added")
            else:
                # Collaboration remains one-sized...
                return BaseResponse(code=200, data="Collaboration added")
        else:
            # Add a new collaboration
            Collaborator(srcUserId=user_id, dstUserId=new_user_id, mutual=False, eventKey=request.eventKey).put()
            return BaseResponse(code=200, data="Collaboration added")

application = endpoints.api_server([MobileAPI])
