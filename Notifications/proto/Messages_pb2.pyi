from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MessageStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PENDING: _ClassVar[MessageStatus]
    SENT: _ClassVar[MessageStatus]
    FAILED: _ClassVar[MessageStatus]

class MessagePriority(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MARKETING: _ClassVar[MessagePriority]
    UTILITY: _ClassVar[MessagePriority]
    AUTHENTICATION: _ClassVar[MessagePriority]
PENDING: MessageStatus
SENT: MessageStatus
FAILED: MessageStatus
MARKETING: MessagePriority
UTILITY: MessagePriority
AUTHENTICATION: MessagePriority

class Variables(_message.Message):
    __slots__ = ("variables",)
    class VariablesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    VARIABLES_FIELD_NUMBER: _ClassVar[int]
    variables: _containers.ScalarMap[str, str]
    def __init__(self, variables: _Optional[_Mapping[str, str]] = ...) -> None: ...

class Recipient(_message.Message):
    __slots__ = ("to_number", "from_number")
    TO_NUMBER_FIELD_NUMBER: _ClassVar[int]
    FROM_NUMBER_FIELD_NUMBER: _ClassVar[int]
    to_number: str
    from_number: str
    def __init__(self, to_number: _Optional[str] = ..., from_number: _Optional[str] = ...) -> None: ...

class MetaData(_message.Message):
    __slots__ = ("request_id", "source_service", "created_at")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_SERVICE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    source_service: str
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, request_id: _Optional[str] = ..., source_service: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class MessageEvent(_message.Message):
    __slots__ = ("template_name", "variables", "recipient")
    TEMPLATE_NAME_FIELD_NUMBER: _ClassVar[int]
    VARIABLES_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_FIELD_NUMBER: _ClassVar[int]
    template_name: str
    variables: Variables
    recipient: Recipient
    def __init__(self, template_name: _Optional[str] = ..., variables: _Optional[_Union[Variables, _Mapping]] = ..., recipient: _Optional[_Union[Recipient, _Mapping]] = ...) -> None: ...

class Error(_message.Message):
    __slots__ = ("error", "error_code")
    ERROR_FIELD_NUMBER: _ClassVar[int]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    error: str
    error_code: str
    def __init__(self, error: _Optional[str] = ..., error_code: _Optional[str] = ...) -> None: ...

class ShortMessage(_message.Message):
    __slots__ = ("id", "to_phone_number", "from_phone_number", "template_name", "status", "variables", "message_type", "created_at", "updated_at", "sent_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    TO_PHONE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    FROM_PHONE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    VARIABLES_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    SENT_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    to_phone_number: str
    from_phone_number: str
    template_name: str
    status: MessageStatus
    variables: str
    message_type: MessagePriority
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    sent_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., to_phone_number: _Optional[str] = ..., from_phone_number: _Optional[str] = ..., template_name: _Optional[str] = ..., status: _Optional[_Union[MessageStatus, str]] = ..., variables: _Optional[str] = ..., message_type: _Optional[_Union[MessagePriority, str]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., sent_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class InvalidMessageEvent(_message.Message):
    __slots__ = ("id", "to_phone_number", "from_phone_number", "template", "message_json", "rendered_message", "error_message", "variables", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    TO_PHONE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    FROM_PHONE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_JSON_FIELD_NUMBER: _ClassVar[int]
    RENDERED_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    VARIABLES_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    to_phone_number: str
    from_phone_number: str
    template: str
    message_json: str
    rendered_message: str
    error_message: str
    variables: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., to_phone_number: _Optional[str] = ..., from_phone_number: _Optional[str] = ..., template: _Optional[str] = ..., message_json: _Optional[str] = ..., rendered_message: _Optional[str] = ..., error_message: _Optional[str] = ..., variables: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Message(_message.Message):
    __slots__ = ("id", "to_phone_number", "from_phone_number", "template_name", "status", "message_json", "rendered_message", "variables", "message_type", "created_at", "updated_at", "sent_at", "error_message")
    ID_FIELD_NUMBER: _ClassVar[int]
    TO_PHONE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    FROM_PHONE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    TEMPLATE_NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_JSON_FIELD_NUMBER: _ClassVar[int]
    RENDERED_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    VARIABLES_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    SENT_AT_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    id: str
    to_phone_number: str
    from_phone_number: str
    template_name: str
    status: MessageStatus
    message_json: str
    rendered_message: str
    variables: str
    message_type: MessagePriority
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    sent_at: _timestamp_pb2.Timestamp
    error_message: str
    def __init__(self, id: _Optional[str] = ..., to_phone_number: _Optional[str] = ..., from_phone_number: _Optional[str] = ..., template_name: _Optional[str] = ..., status: _Optional[_Union[MessageStatus, str]] = ..., message_json: _Optional[str] = ..., rendered_message: _Optional[str] = ..., variables: _Optional[str] = ..., message_type: _Optional[_Union[MessagePriority, str]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., sent_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., error_message: _Optional[str] = ...) -> None: ...

class AddMessageEventRequest(_message.Message):
    __slots__ = ("message_event",)
    MESSAGE_EVENT_FIELD_NUMBER: _ClassVar[int]
    message_event: MessageEvent
    def __init__(self, message_event: _Optional[_Union[MessageEvent, _Mapping]] = ...) -> None: ...

class AddMessageEventResponse(_message.Message):
    __slots__ = ("message", "success", "error")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    message: Message
    success: bool
    error: Error
    def __init__(self, message: _Optional[_Union[Message, _Mapping]] = ..., success: bool = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class UpdateMessageEventRequest(_message.Message):
    __slots__ = ("message_id", "message_event")
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_EVENT_FIELD_NUMBER: _ClassVar[int]
    message_id: str
    message_event: MessageEvent
    def __init__(self, message_id: _Optional[str] = ..., message_event: _Optional[_Union[MessageEvent, _Mapping]] = ...) -> None: ...

class UpdateMessageEventResponse(_message.Message):
    __slots__ = ("message", "success", "error")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    message: Message
    success: bool
    error: Error
    def __init__(self, message: _Optional[_Union[Message, _Mapping]] = ..., success: bool = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class RemoveMessageEventRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class RemoveMessageEventResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: Error
    def __init__(self, success: bool = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class GetMessageEventRequest(_message.Message):
    __slots__ = ("message_id",)
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    message_id: str
    def __init__(self, message_id: _Optional[str] = ...) -> None: ...

class GetMessageEventResponse(_message.Message):
    __slots__ = ("message", "success", "error")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    message: Message
    success: bool
    error: Error
    def __init__(self, message: _Optional[_Union[Message, _Mapping]] = ..., success: bool = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class ListMessageEventRequest(_message.Message):
    __slots__ = ("template_name", "to_phone_number", "from_phone_number", "message_category", "status", "start_date", "end_date", "page", "limit")
    TEMPLATE_NAME_FIELD_NUMBER: _ClassVar[int]
    TO_PHONE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    FROM_PHONE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_CATEGORY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    template_name: str
    to_phone_number: str
    from_phone_number: str
    message_category: MessagePriority
    status: MessageStatus
    start_date: _timestamp_pb2.Timestamp
    end_date: _timestamp_pb2.Timestamp
    page: int
    limit: int
    def __init__(self, template_name: _Optional[str] = ..., to_phone_number: _Optional[str] = ..., from_phone_number: _Optional[str] = ..., message_category: _Optional[_Union[MessagePriority, str]] = ..., status: _Optional[_Union[MessageStatus, str]] = ..., start_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., page: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class ListMessageEventResponse(_message.Message):
    __slots__ = ("messages", "success", "error", "next_page", "previous_page")
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_PAGE_FIELD_NUMBER: _ClassVar[int]
    messages: _containers.RepeatedCompositeFieldContainer[Message]
    success: bool
    error: Error
    next_page: int
    previous_page: int
    def __init__(self, messages: _Optional[_Iterable[_Union[Message, _Mapping]]] = ..., success: bool = ..., error: _Optional[_Union[Error, _Mapping]] = ..., next_page: _Optional[int] = ..., previous_page: _Optional[int] = ...) -> None: ...

class GetMessageRequest(_message.Message):
    __slots__ = ("message_id",)
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    message_id: str
    def __init__(self, message_id: _Optional[str] = ...) -> None: ...

class GetMessageResponse(_message.Message):
    __slots__ = ("message", "success", "error")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    message: ShortMessage
    success: bool
    error: Error
    def __init__(self, message: _Optional[_Union[ShortMessage, _Mapping]] = ..., success: bool = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class DeleteMessageRequest(_message.Message):
    __slots__ = ("message_id",)
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    message_id: str
    def __init__(self, message_id: _Optional[str] = ...) -> None: ...

class DeleteMessageResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: Error
    def __init__(self, success: bool = ..., error: _Optional[_Union[Error, _Mapping]] = ...) -> None: ...

class ListMessageRequest(_message.Message):
    __slots__ = ("template_name", "to_phone_number", "from_phone_number", "message_category", "status", "start_date", "end_date", "page", "limit")
    TEMPLATE_NAME_FIELD_NUMBER: _ClassVar[int]
    TO_PHONE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    FROM_PHONE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_CATEGORY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    template_name: str
    to_phone_number: str
    from_phone_number: str
    message_category: MessagePriority
    status: MessageStatus
    start_date: _timestamp_pb2.Timestamp
    end_date: _timestamp_pb2.Timestamp
    page: int
    limit: int
    def __init__(self, template_name: _Optional[str] = ..., to_phone_number: _Optional[str] = ..., from_phone_number: _Optional[str] = ..., message_category: _Optional[_Union[MessagePriority, str]] = ..., status: _Optional[_Union[MessageStatus, str]] = ..., start_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., page: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class ListMessageResponse(_message.Message):
    __slots__ = ("messages", "success", "error", "next_page", "previous_page")
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_PAGE_FIELD_NUMBER: _ClassVar[int]
    messages: _containers.RepeatedCompositeFieldContainer[ShortMessage]
    success: bool
    error: Error
    next_page: int
    previous_page: int
    def __init__(self, messages: _Optional[_Iterable[_Union[ShortMessage, _Mapping]]] = ..., success: bool = ..., error: _Optional[_Union[Error, _Mapping]] = ..., next_page: _Optional[int] = ..., previous_page: _Optional[int] = ...) -> None: ...

class ListInvalidMessageEventRequest(_message.Message):
    __slots__ = ("template", "to_phone_number", "from_phone_number", "start_date", "end_date", "page", "limit")
    TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    TO_PHONE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    FROM_PHONE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    template: str
    to_phone_number: str
    from_phone_number: str
    start_date: _timestamp_pb2.Timestamp
    end_date: _timestamp_pb2.Timestamp
    page: int
    limit: int
    def __init__(self, template: _Optional[str] = ..., to_phone_number: _Optional[str] = ..., from_phone_number: _Optional[str] = ..., start_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., page: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class ListInvalidMessageEventResponse(_message.Message):
    __slots__ = ("invalid_messages", "success", "error", "next_page", "previous_page")
    INVALID_MESSAGES_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_PAGE_FIELD_NUMBER: _ClassVar[int]
    invalid_messages: _containers.RepeatedCompositeFieldContainer[InvalidMessageEvent]
    success: bool
    error: Error
    next_page: int
    previous_page: int
    def __init__(self, invalid_messages: _Optional[_Iterable[_Union[InvalidMessageEvent, _Mapping]]] = ..., success: bool = ..., error: _Optional[_Union[Error, _Mapping]] = ..., next_page: _Optional[int] = ..., previous_page: _Optional[int] = ...) -> None: ...
