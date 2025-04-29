import annotations_pb2 as _annotations_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Token(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...

class CreateUserRequest(_message.Message):
    __slots__ = ("firebase_uid", "Token")
    FIREBASE_UID_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    firebase_uid: str
    Token: Token
    def __init__(self, firebase_uid: _Optional[str] = ..., Token: _Optional[_Union[Token, _Mapping]] = ...) -> None: ...

class CreateUserResponse(_message.Message):
    __slots__ = ("firebase_uid", "email", "user_uuid")
    FIREBASE_UID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    firebase_uid: str
    email: str
    user_uuid: str
    def __init__(self, firebase_uid: _Optional[str] = ..., email: _Optional[str] = ..., user_uuid: _Optional[str] = ...) -> None: ...

class VerifyTokenResponse(_message.Message):
    __slots__ = ("firebase_uid", "email", "is_valid")
    FIREBASE_UID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    IS_VALID_FIELD_NUMBER: _ClassVar[int]
    firebase_uid: str
    email: str
    is_valid: bool
    def __init__(self, firebase_uid: _Optional[str] = ..., email: _Optional[str] = ..., is_valid: bool = ...) -> None: ...
