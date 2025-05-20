import annotations_pb2 as _annotations_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class user(_message.Message):
    __slots__ = ("user_uuid", "firebase_uid", "email", "stores", "created_at", "updated_at")
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    FIREBASE_UID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    STORES_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    user_uuid: str
    firebase_uid: str
    email: str
    stores: _containers.RepeatedCompositeFieldContainer[store]
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, user_uuid: _Optional[str] = ..., firebase_uid: _Optional[str] = ..., email: _Optional[str] = ..., stores: _Optional[_Iterable[_Union[store, _Mapping]]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class store(_message.Message):
    __slots__ = ("store_uuid", "store_name", "gst_number", "address", "is_active", "is_open", "created_at", "updated_at")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_NAME_FIELD_NUMBER: _ClassVar[int]
    GST_NUMBER_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    IS_OPEN_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    store_name: str
    gst_number: str
    address: address
    is_active: bool
    is_open: bool
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, store_uuid: _Optional[str] = ..., store_name: _Optional[str] = ..., gst_number: _Optional[str] = ..., address: _Optional[_Union[address, _Mapping]] = ..., is_active: bool = ..., is_open: bool = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class address(_message.Message):
    __slots__ = ("address_uuid", "address_line_1", "address_line_2", "landmark", "city", "state", "country", "pincode", "created_at", "updated_at")
    ADDRESS_UUID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_LINE_1_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_LINE_2_FIELD_NUMBER: _ClassVar[int]
    LANDMARK_FIELD_NUMBER: _ClassVar[int]
    CITY_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    PINCODE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    address_uuid: str
    address_line_1: str
    address_line_2: str
    landmark: str
    city: str
    state: str
    country: str
    pincode: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, address_uuid: _Optional[str] = ..., address_line_1: _Optional[str] = ..., address_line_2: _Optional[str] = ..., landmark: _Optional[str] = ..., city: _Optional[str] = ..., state: _Optional[str] = ..., country: _Optional[str] = ..., pincode: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

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

class GetUserRequest(_message.Message):
    __slots__ = ("user_uuid",)
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    user_uuid: str
    def __init__(self, user_uuid: _Optional[str] = ...) -> None: ...

class UpdateUserRequest(_message.Message):
    __slots__ = ("user_uuid", "email", "email_verified")
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    EMAIL_VERIFIED_FIELD_NUMBER: _ClassVar[int]
    user_uuid: str
    email: str
    email_verified: str
    def __init__(self, user_uuid: _Optional[str] = ..., email: _Optional[str] = ..., email_verified: _Optional[str] = ...) -> None: ...

class DeleteUserRequest(_message.Message):
    __slots__ = ("user_uuid",)
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    user_uuid: str
    def __init__(self, user_uuid: _Optional[str] = ...) -> None: ...

class CreateStoreRequest(_message.Message):
    __slots__ = ("user_uuid", "store_name", "gst_number", "is_active", "is_open", "discription")
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_NAME_FIELD_NUMBER: _ClassVar[int]
    GST_NUMBER_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    IS_OPEN_FIELD_NUMBER: _ClassVar[int]
    DISCRIPTION_FIELD_NUMBER: _ClassVar[int]
    user_uuid: str
    store_name: str
    gst_number: str
    is_active: bool
    is_open: bool
    discription: str
    def __init__(self, user_uuid: _Optional[str] = ..., store_name: _Optional[str] = ..., gst_number: _Optional[str] = ..., is_active: bool = ..., is_open: bool = ..., discription: _Optional[str] = ...) -> None: ...

class StoreResponse(_message.Message):
    __slots__ = ("user_uuid", "store")
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_FIELD_NUMBER: _ClassVar[int]
    user_uuid: str
    store: store
    def __init__(self, user_uuid: _Optional[str] = ..., store: _Optional[_Union[store, _Mapping]] = ...) -> None: ...

class UpdateStoreRequest(_message.Message):
    __slots__ = ("user_uuid", "store_uuid", "store_name", "gst_number", "is_active", "is_open")
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_NAME_FIELD_NUMBER: _ClassVar[int]
    GST_NUMBER_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    IS_OPEN_FIELD_NUMBER: _ClassVar[int]
    user_uuid: str
    store_uuid: str
    store_name: str
    gst_number: str
    is_active: bool
    is_open: bool
    def __init__(self, user_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., store_name: _Optional[str] = ..., gst_number: _Optional[str] = ..., is_active: bool = ..., is_open: bool = ...) -> None: ...

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
    __slots__ = ("store_uuid", "address_uuid", "address_1", "address_2", "landmark", "city", "state", "pincode", "country")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_UUID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_1_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_2_FIELD_NUMBER: _ClassVar[int]
    LANDMARK_FIELD_NUMBER: _ClassVar[int]
    CITY_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    PINCODE_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    address_uuid: str
    address_1: str
    address_2: str
    landmark: str
    city: str
    state: str
    pincode: str
    country: str
    def __init__(self, store_uuid: _Optional[str] = ..., address_uuid: _Optional[str] = ..., address_1: _Optional[str] = ..., address_2: _Optional[str] = ..., landmark: _Optional[str] = ..., city: _Optional[str] = ..., state: _Optional[str] = ..., pincode: _Optional[str] = ..., country: _Optional[str] = ...) -> None: ...

class GetStoreRequest(_message.Message):
    __slots__ = ("user_uuid", "store_uuid")
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    user_uuid: str
    store_uuid: str
    def __init__(self, user_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ...) -> None: ...

class GetAllStoreRequest(_message.Message):
    __slots__ = ("user_uuid", "page", "limit")
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    user_uuid: str
    page: str
    limit: str
    def __init__(self, user_uuid: _Optional[str] = ..., page: _Optional[str] = ..., limit: _Optional[str] = ...) -> None: ...

class GetAllStoreResponse(_message.Message):
    __slots__ = ("stores", "prev_page", "next_page")
    STORES_FIELD_NUMBER: _ClassVar[int]
    PREV_PAGE_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_FIELD_NUMBER: _ClassVar[int]
    stores: _containers.RepeatedCompositeFieldContainer[store]
    prev_page: int
    next_page: int
    def __init__(self, stores: _Optional[_Iterable[_Union[store, _Mapping]]] = ..., prev_page: _Optional[int] = ..., next_page: _Optional[int] = ...) -> None: ...

class GetAddressRequest(_message.Message):
    __slots__ = ("user_uuid", "store_uuid", "address_uuid")
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_UUID_FIELD_NUMBER: _ClassVar[int]
    user_uuid: str
    store_uuid: str
    address_uuid: str
    def __init__(self, user_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., address_uuid: _Optional[str] = ...) -> None: ...

class DeleteStoreRequest(_message.Message):
    __slots__ = ("user_uuid", "store_uuid")
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    user_uuid: str
    store_uuid: str
    def __init__(self, user_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ...) -> None: ...

class DeleteAddressRequest(_message.Message):
    __slots__ = ("user_uuid", "store_uuid", "address_uuid")
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_UUID_FIELD_NUMBER: _ClassVar[int]
    user_uuid: str
    store_uuid: str
    address_uuid: str
    def __init__(self, user_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., address_uuid: _Optional[str] = ...) -> None: ...

class AddressResponse(_message.Message):
    __slots__ = ("store_uuid", "address")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    address: address
    def __init__(self, store_uuid: _Optional[str] = ..., address: _Optional[_Union[address, _Mapping]] = ...) -> None: ...

class CreateStoreWithAddressRequest(_message.Message):
    __slots__ = ("user_uuid", "store_name", "gst_number", "address_1", "address_2", "landmark", "city", "state", "pincode", "country")
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_NAME_FIELD_NUMBER: _ClassVar[int]
    GST_NUMBER_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_1_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_2_FIELD_NUMBER: _ClassVar[int]
    LANDMARK_FIELD_NUMBER: _ClassVar[int]
    CITY_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    PINCODE_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    user_uuid: str
    store_name: str
    gst_number: str
    address_1: str
    address_2: str
    landmark: str
    city: str
    state: str
    pincode: str
    country: str
    def __init__(self, user_uuid: _Optional[str] = ..., store_name: _Optional[str] = ..., gst_number: _Optional[str] = ..., address_1: _Optional[str] = ..., address_2: _Optional[str] = ..., landmark: _Optional[str] = ..., city: _Optional[str] = ..., state: _Optional[str] = ..., pincode: _Optional[str] = ..., country: _Optional[str] = ...) -> None: ...
