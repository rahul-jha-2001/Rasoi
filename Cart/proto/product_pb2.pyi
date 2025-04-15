from google.protobuf import timestamp_pb2 as _timestamp_pb2
import annotations_pb2 as _annotations_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Productstatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DRAFT: _ClassVar[Productstatus]
    ACTIVE: _ClassVar[Productstatus]
    INACTIVE: _ClassVar[Productstatus]
DRAFT: Productstatus
ACTIVE: Productstatus
INACTIVE: Productstatus

class category(_message.Message):
    __slots__ = ("category_uuid", "store_uuid", "name", "description", "display_order", "is_available", "is_active", "created_at", "updated_at")
    CATEGORY_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_ORDER_FIELD_NUMBER: _ClassVar[int]
    IS_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    category_uuid: str
    store_uuid: str
    name: str
    description: str
    display_order: int
    is_available: bool
    is_active: bool
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, category_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., display_order: _Optional[int] = ..., is_available: bool = ..., is_active: bool = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class add_on(_message.Message):
    __slots__ = ("add_on_uuid", "name", "is_available", "max_selectable", "GST_percentage", "price", "product_uuid", "created_at", "updated_at")
    ADD_ON_UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    MAX_SELECTABLE_FIELD_NUMBER: _ClassVar[int]
    GST_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_UUID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    add_on_uuid: str
    name: str
    is_available: bool
    max_selectable: int
    GST_percentage: float
    price: float
    product_uuid: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, add_on_uuid: _Optional[str] = ..., name: _Optional[str] = ..., is_available: bool = ..., max_selectable: _Optional[int] = ..., GST_percentage: _Optional[float] = ..., price: _Optional[float] = ..., product_uuid: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class product(_message.Message):
    __slots__ = ("product_uuid", "store_uuid", "name", "description", "status", "is_available", "display_price", "price", "GST_percentage", "category_uuid", "dietary_pref", "image_URL", "created_at", "updated_at")
    PRODUCT_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    IS_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_PRICE_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    GST_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_UUID_FIELD_NUMBER: _ClassVar[int]
    DIETARY_PREF_FIELD_NUMBER: _ClassVar[int]
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    product_uuid: str
    store_uuid: str
    name: str
    description: str
    status: Productstatus
    is_available: bool
    display_price: float
    price: float
    GST_percentage: float
    category_uuid: str
    dietary_pref: str
    image_URL: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, product_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., status: _Optional[_Union[Productstatus, str]] = ..., is_available: bool = ..., display_price: _Optional[float] = ..., price: _Optional[float] = ..., GST_percentage: _Optional[float] = ..., category_uuid: _Optional[str] = ..., dietary_pref: _Optional[str] = ..., image_URL: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class error(_message.Message):
    __slots__ = ("error_message", "error_code")
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    error_message: str
    error_code: str
    def __init__(self, error_message: _Optional[str] = ..., error_code: _Optional[str] = ...) -> None: ...

class CreateCategoryRequest(_message.Message):
    __slots__ = ("store_uuid", "category")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    category: category
    def __init__(self, store_uuid: _Optional[str] = ..., category: _Optional[_Union[category, _Mapping]] = ...) -> None: ...

class CategoryResponse(_message.Message):
    __slots__ = ("category", "success", "error")
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    category: category
    success: bool
    error: error
    def __init__(self, category: _Optional[_Union[category, _Mapping]] = ..., success: bool = ..., error: _Optional[_Union[error, _Mapping]] = ...) -> None: ...

class UpdateCategoryRequest(_message.Message):
    __slots__ = ("store_uuid", "category_uuid", "category")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_UUID_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    category_uuid: str
    category: category
    def __init__(self, store_uuid: _Optional[str] = ..., category_uuid: _Optional[str] = ..., category: _Optional[_Union[category, _Mapping]] = ...) -> None: ...

class GetCategoryRequest(_message.Message):
    __slots__ = ("category_uuid", "store_uuid")
    CATEGORY_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    category_uuid: str
    store_uuid: str
    def __init__(self, category_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ...) -> None: ...

class ListCategoryRequest(_message.Message):
    __slots__ = ("store_uuid", "page", "limit")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    page: int
    limit: int
    def __init__(self, store_uuid: _Optional[str] = ..., page: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class ListCategoryResponse(_message.Message):
    __slots__ = ("categories", "prev_page", "next_page", "success", "error")
    CATEGORIES_FIELD_NUMBER: _ClassVar[int]
    PREV_PAGE_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    categories: _containers.RepeatedCompositeFieldContainer[category]
    prev_page: int
    next_page: int
    success: bool
    error: error
    def __init__(self, categories: _Optional[_Iterable[_Union[category, _Mapping]]] = ..., prev_page: _Optional[int] = ..., next_page: _Optional[int] = ..., success: bool = ..., error: _Optional[_Union[error, _Mapping]] = ...) -> None: ...

class DeleteCategoryRequest(_message.Message):
    __slots__ = ("category_uuid", "store_uuid")
    CATEGORY_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    category_uuid: str
    store_uuid: str
    def __init__(self, category_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ...) -> None: ...

class DeleteCategoryResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: error
    def __init__(self, success: bool = ..., error: _Optional[_Union[error, _Mapping]] = ...) -> None: ...

class CreateProductRequest(_message.Message):
    __slots__ = ("product", "Image", "store_uuid", "category_uuid")
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_UUID_FIELD_NUMBER: _ClassVar[int]
    product: product
    Image: bytes
    store_uuid: str
    category_uuid: str
    def __init__(self, product: _Optional[_Union[product, _Mapping]] = ..., Image: _Optional[bytes] = ..., store_uuid: _Optional[str] = ..., category_uuid: _Optional[str] = ...) -> None: ...

class ProductResponse(_message.Message):
    __slots__ = ("product", "success", "error")
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    product: product
    success: bool
    error: error
    def __init__(self, product: _Optional[_Union[product, _Mapping]] = ..., success: bool = ..., error: _Optional[_Union[error, _Mapping]] = ...) -> None: ...

class GetProductRequest(_message.Message):
    __slots__ = ("product_uuid", "store_uuid", "category_uuid")
    PRODUCT_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_UUID_FIELD_NUMBER: _ClassVar[int]
    product_uuid: str
    store_uuid: str
    category_uuid: str
    def __init__(self, product_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., category_uuid: _Optional[str] = ...) -> None: ...

class UpdateProductRequest(_message.Message):
    __slots__ = ("product_uuid", "store_uuid", "product", "image", "category_uuid")
    PRODUCT_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_UUID_FIELD_NUMBER: _ClassVar[int]
    product_uuid: str
    store_uuid: str
    product: product
    image: bytes
    category_uuid: str
    def __init__(self, product_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., product: _Optional[_Union[product, _Mapping]] = ..., image: _Optional[bytes] = ..., category_uuid: _Optional[str] = ...) -> None: ...

class DeleteProductRequest(_message.Message):
    __slots__ = ("product_uuid", "store_uuid", "category_uuid")
    PRODUCT_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_UUID_FIELD_NUMBER: _ClassVar[int]
    product_uuid: str
    store_uuid: str
    category_uuid: str
    def __init__(self, product_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., category_uuid: _Optional[str] = ...) -> None: ...

class DeleteProductResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: error
    def __init__(self, success: bool = ..., error: _Optional[_Union[error, _Mapping]] = ...) -> None: ...

class ListProductsRequest(_message.Message):
    __slots__ = ("store_uuid", "category_uuid", "page", "limit")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_UUID_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    category_uuid: str
    page: int
    limit: int
    def __init__(self, store_uuid: _Optional[str] = ..., category_uuid: _Optional[str] = ..., page: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class ListProductsResponse(_message.Message):
    __slots__ = ("products", "success", "error", "prev_page", "next_page")
    PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    PREV_PAGE_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_FIELD_NUMBER: _ClassVar[int]
    products: _containers.RepeatedCompositeFieldContainer[product]
    success: bool
    error: error
    prev_page: int
    next_page: int
    def __init__(self, products: _Optional[_Iterable[_Union[product, _Mapping]]] = ..., success: bool = ..., error: _Optional[_Union[error, _Mapping]] = ..., prev_page: _Optional[int] = ..., next_page: _Optional[int] = ...) -> None: ...

class CreateAddOnRequest(_message.Message):
    __slots__ = ("store_uuid", "product_uuid", "add_on")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_UUID_FIELD_NUMBER: _ClassVar[int]
    ADD_ON_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    product_uuid: str
    add_on: add_on
    def __init__(self, store_uuid: _Optional[str] = ..., product_uuid: _Optional[str] = ..., add_on: _Optional[_Union[add_on, _Mapping]] = ...) -> None: ...

class AddOnResponse(_message.Message):
    __slots__ = ("add_on", "success", "error")
    ADD_ON_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    add_on: add_on
    success: bool
    error: error
    def __init__(self, add_on: _Optional[_Union[add_on, _Mapping]] = ..., success: bool = ..., error: _Optional[_Union[error, _Mapping]] = ...) -> None: ...

class GetAddOnRequest(_message.Message):
    __slots__ = ("store_uuid", "product_uuid", "add_on_uuid")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_UUID_FIELD_NUMBER: _ClassVar[int]
    ADD_ON_UUID_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    product_uuid: str
    add_on_uuid: str
    def __init__(self, store_uuid: _Optional[str] = ..., product_uuid: _Optional[str] = ..., add_on_uuid: _Optional[str] = ...) -> None: ...

class UpdateAddOnRequest(_message.Message):
    __slots__ = ("store_uuid", "product_uuid", "add_on_uuid", "add_on")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_UUID_FIELD_NUMBER: _ClassVar[int]
    ADD_ON_UUID_FIELD_NUMBER: _ClassVar[int]
    ADD_ON_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    product_uuid: str
    add_on_uuid: str
    add_on: add_on
    def __init__(self, store_uuid: _Optional[str] = ..., product_uuid: _Optional[str] = ..., add_on_uuid: _Optional[str] = ..., add_on: _Optional[_Union[add_on, _Mapping]] = ...) -> None: ...

class DeleteAddOnRequest(_message.Message):
    __slots__ = ("add_on_uuid", "store_uuid", "product_uuid")
    ADD_ON_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_UUID_FIELD_NUMBER: _ClassVar[int]
    add_on_uuid: str
    store_uuid: str
    product_uuid: str
    def __init__(self, add_on_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., product_uuid: _Optional[str] = ...) -> None: ...

class DeleteAddOnResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: error
    def __init__(self, success: bool = ..., error: _Optional[_Union[error, _Mapping]] = ...) -> None: ...

class ListAddOnRequest(_message.Message):
    __slots__ = ("product_uuid", "store_uuid", "page", "limit")
    PRODUCT_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    product_uuid: str
    store_uuid: str
    page: int
    limit: int
    def __init__(self, product_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., page: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class ListAddOnResponse(_message.Message):
    __slots__ = ("add_ons", "success", "error", "next_page", "prev_page")
    ADD_ONS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_FIELD_NUMBER: _ClassVar[int]
    PREV_PAGE_FIELD_NUMBER: _ClassVar[int]
    add_ons: _containers.RepeatedCompositeFieldContainer[add_on]
    success: bool
    error: error
    next_page: int
    prev_page: int
    def __init__(self, add_ons: _Optional[_Iterable[_Union[add_on, _Mapping]]] = ..., success: bool = ..., error: _Optional[_Union[error, _Mapping]] = ..., next_page: _Optional[int] = ..., prev_page: _Optional[int] = ...) -> None: ...
