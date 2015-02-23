from protorpc import messages


class RegistrationRequest(messages.Message):
    operating_system = messages.StringField(1, required=True)
    mobile_id = messages.StringField(2, required=True)
    name = messages.StringField(3, required=False, default='Unnamed Device')
    device_uuid = messages.StringField(4, required=True)


class NoteMessage(messages.Message):
    noteUID = messages.StringField(1, required=True)
    refKeys = messages.StringField(2, required=True)
    content = messages.StringField(3, default="")
    last_update = messages.IntegerField(9)
    last_update_user = messages.StringField(10)


class BaseResponse(messages.Message):
    code = messages.IntegerField(1)
    data = messages.StringField(2)


class NoteResponse(messages.Message):
    response = messages.MessageField(BaseResponse, 1)
    note = messages.MessageField(NoteMessage, 2)


class NoteListResponse(messages.Message):
    response = messages.MessageField(BaseResponse, 1)
    note = messages.MessageField(NoteMessage, 2, repeated=True)


class CollaboratorAdd(messages.Message):
    eventKey = messages.StringField(1, required=True)
    email = messages.StringField(2, required=True)


class CollaboratorRemove(messages.Message):
    eventKey = messages.StringField(1, required=True)
    email = messages.StringField(2, required=True)


class ListCollaborators(messages.Message):
    response = messages.MessageField(BaseResponse, 1)
    collaberators = messages.StringField(2, repeated=True)
