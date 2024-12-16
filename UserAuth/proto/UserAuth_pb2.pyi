from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Token(_message.Message):
    __slots__ = ("access", "refresh")
    ACCESS_FIELD_NUMBER: _ClassVar[int]
    REFRESH_FIELD_NUMBER: _ClassVar[int]
    access: str
    refresh: str
    def __init__(self, access: _Optional[str] = ..., refresh: _Optional[str] = ...) -> None: ...

class OTPRequest(_message.Message):
    __slots__ = ("PhoneNumber", "UserName", "StoreUuid")
    PHONENUMBER_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    STOREUUID_FIELD_NUMBER: _ClassVar[int]
    PhoneNumber: str
    UserName: str
    StoreUuid: str
    def __init__(self, PhoneNumber: _Optional[str] = ..., UserName: _Optional[str] = ..., StoreUuid: _Optional[str] = ...) -> None: ...

class VerifyOTPRequest(_message.Message):
    __slots__ = ("PhoneNumber", "UserName", "StoreUuid", "OTP")
    PHONENUMBER_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    STOREUUID_FIELD_NUMBER: _ClassVar[int]
    OTP_FIELD_NUMBER: _ClassVar[int]
    PhoneNumber: str
    UserName: str
    StoreUuid: str
    OTP: str
    def __init__(self, PhoneNumber: _Optional[str] = ..., UserName: _Optional[str] = ..., StoreUuid: _Optional[str] = ..., OTP: _Optional[str] = ...) -> None: ...

class OTPResponse(_message.Message):
    __slots__ = ("Success", "message", "CreatedAt")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    Success: bool
    message: str
    CreatedAt: _timestamp_pb2.Timestamp
    def __init__(self, Success: bool = ..., message: _Optional[str] = ..., CreatedAt: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class AuthResponse(_message.Message):
    __slots__ = ("authenticated", "JWTtoken", "message")
    AUTHENTICATED_FIELD_NUMBER: _ClassVar[int]
    JWTTOKEN_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    authenticated: bool
    JWTtoken: Token
    message: str
    def __init__(self, authenticated: bool = ..., JWTtoken: _Optional[_Union[Token, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class CreateStoreRequest(_message.Message):
    __slots__ = ("Email", "Password", "PhoneNumber", "StoreName", "StoreAddress", "GSTNumber")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    PHONENUMBER_FIELD_NUMBER: _ClassVar[int]
    STORENAME_FIELD_NUMBER: _ClassVar[int]
    STOREADDRESS_FIELD_NUMBER: _ClassVar[int]
    GSTNUMBER_FIELD_NUMBER: _ClassVar[int]
    Email: str
    Password: str
    PhoneNumber: str
    StoreName: str
    StoreAddress: str
    GSTNumber: str
    def __init__(self, Email: _Optional[str] = ..., Password: _Optional[str] = ..., PhoneNumber: _Optional[str] = ..., StoreName: _Optional[str] = ..., StoreAddress: _Optional[str] = ..., GSTNumber: _Optional[str] = ...) -> None: ...

class CreateStoreResponse(_message.Message):
    __slots__ = ("success", "StoreUuid", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    STOREUUID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    StoreUuid: str
    message: str
    def __init__(self, success: bool = ..., StoreUuid: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class AuthStoreRequest(_message.Message):
    __slots__ = ("Email", "Password")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    Email: str
    Password: str
    def __init__(self, Email: _Optional[str] = ..., Password: _Optional[str] = ...) -> None: ...

class AuthStoreResponse(_message.Message):
    __slots__ = ("Authenticated", "StoreUuid", "JWTToken", "message")
    AUTHENTICATED_FIELD_NUMBER: _ClassVar[int]
    STOREUUID_FIELD_NUMBER: _ClassVar[int]
    JWTTOKEN_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    Authenticated: bool
    StoreUuid: str
    JWTToken: Token
    message: str
    def __init__(self, Authenticated: bool = ..., StoreUuid: _Optional[str] = ..., JWTToken: _Optional[_Union[Token, _Mapping]] = ..., message: _Optional[str] = ...) -> None: ...

class UpdateStoreRequest(_message.Message):
    __slots__ = ("StoreUuid", "PhoneNumber", "StoreName", "StoreAddress", "GSTNumber")
    STOREUUID_FIELD_NUMBER: _ClassVar[int]
    PHONENUMBER_FIELD_NUMBER: _ClassVar[int]
    STORENAME_FIELD_NUMBER: _ClassVar[int]
    STOREADDRESS_FIELD_NUMBER: _ClassVar[int]
    GSTNUMBER_FIELD_NUMBER: _ClassVar[int]
    StoreUuid: str
    PhoneNumber: str
    StoreName: str
    StoreAddress: str
    GSTNumber: str
    def __init__(self, StoreUuid: _Optional[str] = ..., PhoneNumber: _Optional[str] = ..., StoreName: _Optional[str] = ..., StoreAddress: _Optional[str] = ..., GSTNumber: _Optional[str] = ...) -> None: ...

class UpdateStoreResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...
