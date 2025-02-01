from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Channel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CHANNEL_UNSPECIFIED: _ClassVar[Channel]
    EMAIL: _ClassVar[Channel]
    SMS: _ClassVar[Channel]
    PUSH: _ClassVar[Channel]
    INAPP: _ClassVar[Channel]
    WHATSAPP: _ClassVar[Channel]
CHANNEL_UNSPECIFIED: Channel
EMAIL: Channel
SMS: Channel
PUSH: Channel
INAPP: Channel
WHATSAPP: Channel

class NotificationMessage(_message.Message):
    __slots__ = ("template_name", "channel", "to_address", "from_address", "variables")
    class VariablesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TEMPLATE_NAME_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    TO_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    FROM_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    VARIABLES_FIELD_NUMBER: _ClassVar[int]
    template_name: str
    channel: Channel
    to_address: str
    from_address: str
    variables: _containers.ScalarMap[str, str]
    def __init__(self, template_name: _Optional[str] = ..., channel: _Optional[_Union[Channel, str]] = ..., to_address: _Optional[str] = ..., from_address: _Optional[str] = ..., variables: _Optional[_Mapping[str, str]] = ...) -> None: ...

    