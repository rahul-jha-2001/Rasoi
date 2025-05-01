import annotations_pb2 as _annotations_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class User(_message.Message):
    __slots__ = ("user_uuid", "firebase_uid", "email", "email_verified", "stores")
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    FIREBASE_UID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    EMAIL_VERIFIED_FIELD_NUMBER: _ClassVar[int]
    STORES_FIELD_NUMBER: _ClassVar[int]
    user_uuid: str
    firebase_uid: str
    email: str
    email_verified: str
    stores: _containers.RepeatedCompositeFieldContainer[store]
    def __init__(self, user_uuid: _Optional[str] = ..., firebase_uid: _Optional[str] = ..., email: _Optional[str] = ..., email_verified: _Optional[str] = ..., stores: _Optional[_Iterable[_Union[store, _Mapping]]] = ...) -> None: ...

class store(_message.Message):
    __slots__ = ("store_uuid", "Store_name", "gst_number", "address")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_NAME_FIELD_NUMBER: _ClassVar[int]
    GST_NUMBER_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    Store_name: str
    gst_number: str
    address: address
    def __init__(self, store_uuid: _Optional[str] = ..., Store_name: _Optional[str] = ..., gst_number: _Optional[str] = ..., address: _Optional[_Union[address, _Mapping]] = ...) -> None: ...

class address(_message.Message):
    __slots__ = ("address_uuid", "address_line_1", "address_line_2", "landmark", "city", "state", "country", "pincode")
    ADDRESS_UUID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_LINE_1_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_LINE_2_FIELD_NUMBER: _ClassVar[int]
    LANDMARK_FIELD_NUMBER: _ClassVar[int]
    CITY_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    PINCODE_FIELD_NUMBER: _ClassVar[int]
    address_uuid: str
    address_line_1: str
    address_line_2: str
    landmark: str
    city: str
    state: str
    country: str
    pincode: str
    def __init__(self, address_uuid: _Optional[str] = ..., address_line_1: _Optional[str] = ..., address_line_2: _Optional[str] = ..., landmark: _Optional[str] = ..., city: _Optional[str] = ..., state: _Optional[str] = ..., country: _Optional[str] = ..., pincode: _Optional[str] = ...) -> None: ...

class VerifyTokenRequest(_message.Message):
    __slots__ = ("token", "firebase_uid")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    FIREBASE_UID_FIELD_NUMBER: _ClassVar[int]
    token: str
    firebase_uid: str
    def __init__(self, token: _Optional[str] = ..., firebase_uid: _Optional[str] = ...) -> None: ...

class CreateUserRequest(_message.Message):
    __slots__ = ("firebase_uid", "token")
    FIREBASE_UID_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    firebase_uid: str
    token: str
    def __init__(self, firebase_uid: _Optional[str] = ..., token: _Optional[str] = ...) -> None: ...

class CreateStoreRequest(_message.Message):
    __slots__ = ("user_uuid", "store_name", "gst_number")
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_NAME_FIELD_NUMBER: _ClassVar[int]
    GST_NUMBER_FIELD_NUMBER: _ClassVar[int]
    user_uuid: str
    store_name: str
    gst_number: str
    def __init__(self, user_uuid: _Optional[str] = ..., store_name: _Optional[str] = ..., gst_number: _Optional[str] = ...) -> None: ...

class StoreResponse(_message.Message):
    __slots__ = ("user_uuid", "store")
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_FIELD_NUMBER: _ClassVar[int]
    user_uuid: str
    store: store
    def __init__(self, user_uuid: _Optional[str] = ..., store: _Optional[_Union[store, _Mapping]] = ...) -> None: ...

class UpdateStoreRequest(_message.Message):
    __slots__ = ("user_uuid", "store_uuid", "store_name", "gst_number")
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_NAME_FIELD_NUMBER: _ClassVar[int]
    GST_NUMBER_FIELD_NUMBER: _ClassVar[int]
    user_uuid: str
    store_uuid: str
    store_name: str
    gst_number: str
    def __init__(self, user_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., store_name: _Optional[str] = ..., gst_number: _Optional[str] = ...) -> None: ...

class AddAddressRequest(_message.Message):
    __slots__ = ("user_uuid", "store_uuid", "address_1", "address_2", "landmark", "city", "state", "pincode", "country")
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_1_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_2_FIELD_NUMBER: _ClassVar[int]
    LANDMARK_FIELD_NUMBER: _ClassVar[int]
    CITY_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    PINCODE_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    user_uuid: str
    store_uuid: str
    address_1: str
    address_2: str
    landmark: str
    city: str
    state: str
    pincode: str
    country: str
    def __init__(self, user_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., address_1: _Optional[str] = ..., address_2: _Optional[str] = ..., landmark: _Optional[str] = ..., city: _Optional[str] = ..., state: _Optional[str] = ..., pincode: _Optional[str] = ..., country: _Optional[str] = ...) -> None: ...

class UpdateAddressRequest(_message.Message):
    __slots__ = ("user_uuid", "store_uuid", "address_uuid", "address_1", "address_2", "landmark", "city", "state", "pincode", "country")
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_UUID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_1_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_2_FIELD_NUMBER: _ClassVar[int]
    LANDMARK_FIELD_NUMBER: _ClassVar[int]
    CITY_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    PINCODE_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    user_uuid: str
    store_uuid: str
    address_uuid: str
    address_1: str
    address_2: str
    landmark: str
    city: str
    state: str
    pincode: str
    country: str
    def __init__(self, user_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., address_uuid: _Optional[str] = ..., address_1: _Optional[str] = ..., address_2: _Optional[str] = ..., landmark: _Optional[str] = ..., city: _Optional[str] = ..., state: _Optional[str] = ..., pincode: _Optional[str] = ..., country: _Optional[str] = ...) -> None: ...
