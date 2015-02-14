from protorpc import messages


class RegistrationRequest(messages.Message):
    operating_system = messages.StringField(1, required=True)
    mobile_id = messages.StringField(2, required=True)
    name = messages.StringField(3, required=False, default='Unnamed Device')
    device_uuid = messages.StringField(4, required=True)


class NoteMessage(messages.Message):
    owner = messages.StringField(1, required=True)
    can_read = messages.StringField(2, repeated=True)
    can_write = messages.StringField(3, repeated=True)
    backend_id = messages.IntegerField(4, required=True)
    content = messages.StringField(5)
    event_key = messages.StringField(6)
    match_key = messages.StringField(7)
    team_key = messages.StringField(8)
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
