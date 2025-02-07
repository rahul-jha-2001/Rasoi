from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

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

class recipient(_message.Message):
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

class NotificationMessage(_message.Message):
    __slots__ = ("template_name", "variables", "recipient", "meta_data")
    TEMPLATE_NAME_FIELD_NUMBER: _ClassVar[int]
    VARIABLES_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_FIELD_NUMBER: _ClassVar[int]
    META_DATA_FIELD_NUMBER: _ClassVar[int]
    template_name: str
    variables: Variables
    recipient: recipient
    meta_data: MetaData
    def __init__(self, template_name: _Optional[str] = ..., variables: _Optional[_Union[Variables, _Mapping]] = ..., recipient: _Optional[_Union[recipient, _Mapping]] = ..., meta_data: _Optional[_Union[MetaData, _Mapping]] = ...) -> None: ...
