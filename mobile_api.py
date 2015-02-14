import ConfigParser
import endpoints
import os

from protorpc import remote

from models.mobile_messages import RegistrationRequest, NoteMessage, BaseResponse, NoteResponse, NoteListResponse

config = ConfigParser.ConfigParser()
config.readfp(open('config.ini'))

client_id_sitevar = config.get('endpoints', 'webId')
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
client_ids.append(endpoints.API_EXPLORER_CLIENT_ID)


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
            return BaseResponse(code=401, message="Unauthorized to register")
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
                parent=ndb.Key(Account, userId),
                user_id=userId,
                messaging_id=gcmId,
                client_type=os,
                device_uuid=uuid,
                display_name=name).put()
            return BaseResponse(code=200, message="Registration successful")
        else:
            # Record already exists, update it
            client = query.fetch(1)[0]
            client.messaging_id = gcmId
            client.display_name = name
            client.put()
            return BaseResponse(code=304, message="Client already exists")

application = endpoints.api_server([MobileAPI])
