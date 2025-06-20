from google.protobuf import timestamp_pb2 as _timestamp_pb2
import annotations_pb2 as _annotations_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Productstatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PRODUCT_STATE_DRAFT: _ClassVar[Productstatus]
    PRODUCT_STATE_ACTIVE: _ClassVar[Productstatus]
    PRODUCT_STATE_INACTIVE: _ClassVar[Productstatus]
    PRODUCT_STATE_OUT_OF_STOCK: _ClassVar[Productstatus]
PRODUCT_STATE_DRAFT: Productstatus
PRODUCT_STATE_ACTIVE: Productstatus
PRODUCT_STATE_INACTIVE: Productstatus
PRODUCT_STATE_OUT_OF_STOCK: Productstatus

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
    __slots__ = ("add_on_uuid", "name", "is_available", "max_selectable", "GST_percentage", "price", "product_uuid", "created_at", "updated_at", "is_free")
    ADD_ON_UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    MAX_SELECTABLE_FIELD_NUMBER: _ClassVar[int]
    GST_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_UUID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    IS_FREE_FIELD_NUMBER: _ClassVar[int]
    add_on_uuid: str
    name: str
    is_available: bool
    max_selectable: int
    GST_percentage: float
    price: float
    product_uuid: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    is_free: bool
    def __init__(self, add_on_uuid: _Optional[str] = ..., name: _Optional[str] = ..., is_available: bool = ..., max_selectable: _Optional[int] = ..., GST_percentage: _Optional[float] = ..., price: _Optional[float] = ..., product_uuid: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., is_free: bool = ...) -> None: ...

class product(_message.Message):
    __slots__ = ("product_uuid", "store_uuid", "name", "description", "status", "is_available", "display_price", "price", "GST_percentage", "category", "dietary_pref", "image_URL", "add_ons", "created_at", "updated_at", "packaging_cost")
    PRODUCT_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    IS_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_PRICE_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    GST_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    DIETARY_PREF_FIELD_NUMBER: _ClassVar[int]
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    ADD_ONS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    PACKAGING_COST_FIELD_NUMBER: _ClassVar[int]
    product_uuid: str
    store_uuid: str
    name: str
    description: str
    status: Productstatus
    is_available: bool
    display_price: float
    price: float
    GST_percentage: float
    category: category
    dietary_pref: _containers.RepeatedCompositeFieldContainer[dietary_preference]
    image_URL: str
    add_ons: _containers.RepeatedCompositeFieldContainer[add_on]
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    packaging_cost: float
    def __init__(self, product_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., status: _Optional[_Union[Productstatus, str]] = ..., is_available: bool = ..., display_price: _Optional[float] = ..., price: _Optional[float] = ..., GST_percentage: _Optional[float] = ..., category: _Optional[_Union[category, _Mapping]] = ..., dietary_pref: _Optional[_Iterable[_Union[dietary_preference, _Mapping]]] = ..., image_URL: _Optional[str] = ..., add_ons: _Optional[_Iterable[_Union[add_on, _Mapping]]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., packaging_cost: _Optional[float] = ...) -> None: ...

class dietary_preference(_message.Message):
    __slots__ = ("store_uuid", "diet_pref_uuid", "name", "description", "icon_url")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    DIET_PREF_UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ICON_URL_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    diet_pref_uuid: str
    name: str
    description: str
    icon_url: str
    def __init__(self, store_uuid: _Optional[str] = ..., diet_pref_uuid: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., icon_url: _Optional[str] = ...) -> None: ...

class CreateCategoryRequest(_message.Message):
    __slots__ = ("store_uuid", "name", "description", "display_order", "is_available", "is_active")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_ORDER_FIELD_NUMBER: _ClassVar[int]
    IS_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    name: str
    description: str
    display_order: int
    is_available: bool
    is_active: bool
    def __init__(self, store_uuid: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., display_order: _Optional[int] = ..., is_available: bool = ..., is_active: bool = ...) -> None: ...

class CategoryResponse(_message.Message):
    __slots__ = ("category",)
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    category: category
    def __init__(self, category: _Optional[_Union[category, _Mapping]] = ...) -> None: ...

class UpdateCategoryRequest(_message.Message):
    __slots__ = ("store_uuid", "category_uuid", "name", "description", "display_order", "is_available", "is_active")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_ORDER_FIELD_NUMBER: _ClassVar[int]
    IS_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    category_uuid: str
    name: str
    description: str
    display_order: int
    is_available: bool
    is_active: bool
    def __init__(self, store_uuid: _Optional[str] = ..., category_uuid: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., display_order: _Optional[int] = ..., is_available: bool = ..., is_active: bool = ...) -> None: ...

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
    __slots__ = ("categories", "prev_page", "next_page")
    CATEGORIES_FIELD_NUMBER: _ClassVar[int]
    PREV_PAGE_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_FIELD_NUMBER: _ClassVar[int]
    categories: _containers.RepeatedCompositeFieldContainer[category]
    prev_page: int
    next_page: int
    def __init__(self, categories: _Optional[_Iterable[_Union[category, _Mapping]]] = ..., prev_page: _Optional[int] = ..., next_page: _Optional[int] = ...) -> None: ...

class DeleteCategoryRequest(_message.Message):
    __slots__ = ("category_uuid", "store_uuid")
    CATEGORY_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    category_uuid: str
    store_uuid: str
    def __init__(self, category_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ...) -> None: ...

class CreateProductRequest(_message.Message):
    __slots__ = ("store_uuid", "name", "description", "status", "is_available", "display_price", "price", "GST_percentage", "category_uuid", "diet_pref_uuid", "image_bytes", "packaging_cost")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    IS_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_PRICE_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    GST_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_UUID_FIELD_NUMBER: _ClassVar[int]
    DIET_PREF_UUID_FIELD_NUMBER: _ClassVar[int]
    IMAGE_BYTES_FIELD_NUMBER: _ClassVar[int]
    PACKAGING_COST_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    name: str
    description: str
    status: Productstatus
    is_available: bool
    display_price: float
    price: float
    GST_percentage: float
    category_uuid: str
    diet_pref_uuid: str
    image_bytes: bytes
    packaging_cost: float
    def __init__(self, store_uuid: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., status: _Optional[_Union[Productstatus, str]] = ..., is_available: bool = ..., display_price: _Optional[float] = ..., price: _Optional[float] = ..., GST_percentage: _Optional[float] = ..., category_uuid: _Optional[str] = ..., diet_pref_uuid: _Optional[str] = ..., image_bytes: _Optional[bytes] = ..., packaging_cost: _Optional[float] = ...) -> None: ...

class ProductResponse(_message.Message):
    __slots__ = ("product",)
    PRODUCT_FIELD_NUMBER: _ClassVar[int]
    product: product
    def __init__(self, product: _Optional[_Union[product, _Mapping]] = ...) -> None: ...

class GetProductRequest(_message.Message):
    __slots__ = ("product_uuid", "store_uuid", "category_uuid", "is_active", "is_available")
    PRODUCT_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_UUID_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    IS_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    product_uuid: str
    store_uuid: str
    category_uuid: str
    is_active: bool
    is_available: bool
    def __init__(self, product_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., category_uuid: _Optional[str] = ..., is_active: bool = ..., is_available: bool = ...) -> None: ...

class UpdateProductRequest(_message.Message):
    __slots__ = ("product_uuid", "store_uuid", "category_uuid", "name", "description", "status", "is_available", "display_price", "price", "GST_percentage", "new_category_uuid", "diet_pref_uuid", "image_bytes", "packaging_cost")
    PRODUCT_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    IS_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_PRICE_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    GST_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    NEW_CATEGORY_UUID_FIELD_NUMBER: _ClassVar[int]
    DIET_PREF_UUID_FIELD_NUMBER: _ClassVar[int]
    IMAGE_BYTES_FIELD_NUMBER: _ClassVar[int]
    PACKAGING_COST_FIELD_NUMBER: _ClassVar[int]
    product_uuid: str
    store_uuid: str
    category_uuid: str
    name: str
    description: str
    status: Productstatus
    is_available: bool
    display_price: float
    price: float
    GST_percentage: float
    new_category_uuid: str
    diet_pref_uuid: str
    image_bytes: bytes
    packaging_cost: float
    def __init__(self, product_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., category_uuid: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., status: _Optional[_Union[Productstatus, str]] = ..., is_available: bool = ..., display_price: _Optional[float] = ..., price: _Optional[float] = ..., GST_percentage: _Optional[float] = ..., new_category_uuid: _Optional[str] = ..., diet_pref_uuid: _Optional[str] = ..., image_bytes: _Optional[bytes] = ..., packaging_cost: _Optional[float] = ...) -> None: ...

class DeleteProductRequest(_message.Message):
    __slots__ = ("product_uuid", "store_uuid", "category_uuid")
    PRODUCT_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_UUID_FIELD_NUMBER: _ClassVar[int]
    product_uuid: str
    store_uuid: str
    category_uuid: str
    def __init__(self, product_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., category_uuid: _Optional[str] = ...) -> None: ...

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
    __slots__ = ("products", "prev_page", "next_page")
    PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    PREV_PAGE_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_FIELD_NUMBER: _ClassVar[int]
    products: _containers.RepeatedCompositeFieldContainer[product]
    prev_page: int
    next_page: int
    def __init__(self, products: _Optional[_Iterable[_Union[product, _Mapping]]] = ..., prev_page: _Optional[int] = ..., next_page: _Optional[int] = ...) -> None: ...

class CreateAddOnRequest(_message.Message):
    __slots__ = ("store_uuid", "product_uuid", "name", "is_available", "max_selectable", "GST_percentage", "price", "is_free")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    MAX_SELECTABLE_FIELD_NUMBER: _ClassVar[int]
    GST_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    IS_FREE_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    product_uuid: str
    name: str
    is_available: bool
    max_selectable: int
    GST_percentage: float
    price: float
    is_free: bool
    def __init__(self, store_uuid: _Optional[str] = ..., product_uuid: _Optional[str] = ..., name: _Optional[str] = ..., is_available: bool = ..., max_selectable: _Optional[int] = ..., GST_percentage: _Optional[float] = ..., price: _Optional[float] = ..., is_free: bool = ...) -> None: ...

class AddOnResponse(_message.Message):
    __slots__ = ("add_on",)
    ADD_ON_FIELD_NUMBER: _ClassVar[int]
    add_on: add_on
    def __init__(self, add_on: _Optional[_Union[add_on, _Mapping]] = ...) -> None: ...

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
    __slots__ = ("store_uuid", "product_uuid", "add_on_uuid", "name", "is_available", "max_selectable", "GST_percentage", "price", "is_free")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_UUID_FIELD_NUMBER: _ClassVar[int]
    ADD_ON_UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    MAX_SELECTABLE_FIELD_NUMBER: _ClassVar[int]
    GST_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    IS_FREE_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    product_uuid: str
    add_on_uuid: str
    name: str
    is_available: bool
    max_selectable: int
    GST_percentage: float
    price: float
    is_free: bool
    def __init__(self, store_uuid: _Optional[str] = ..., product_uuid: _Optional[str] = ..., add_on_uuid: _Optional[str] = ..., name: _Optional[str] = ..., is_available: bool = ..., max_selectable: _Optional[int] = ..., GST_percentage: _Optional[float] = ..., price: _Optional[float] = ..., is_free: bool = ...) -> None: ...

class DeleteAddOnRequest(_message.Message):
    __slots__ = ("add_on_uuid", "store_uuid", "product_uuid")
    ADD_ON_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_UUID_FIELD_NUMBER: _ClassVar[int]
    add_on_uuid: str
    store_uuid: str
    product_uuid: str
    def __init__(self, add_on_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., product_uuid: _Optional[str] = ...) -> None: ...

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
    __slots__ = ("add_ons", "next_page", "prev_page")
    ADD_ONS_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_FIELD_NUMBER: _ClassVar[int]
    PREV_PAGE_FIELD_NUMBER: _ClassVar[int]
    add_ons: _containers.RepeatedCompositeFieldContainer[add_on]
    next_page: int
    prev_page: int
    def __init__(self, add_ons: _Optional[_Iterable[_Union[add_on, _Mapping]]] = ..., next_page: _Optional[int] = ..., prev_page: _Optional[int] = ...) -> None: ...

class CreateDietaryPreference(_message.Message):
    __slots__ = ("store_uuid", "name", "description", "icon_image_bytes")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ICON_IMAGE_BYTES_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    name: str
    description: str
    icon_image_bytes: bytes
    def __init__(self, store_uuid: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., icon_image_bytes: _Optional[bytes] = ...) -> None: ...

class GetDietaryPreference(_message.Message):
    __slots__ = ("store_uuid", "diet_pref_uuid")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    DIET_PREF_UUID_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    diet_pref_uuid: str
    def __init__(self, store_uuid: _Optional[str] = ..., diet_pref_uuid: _Optional[str] = ...) -> None: ...

class DietPrefResponse(_message.Message):
    __slots__ = ("dietary_preference",)
    DIETARY_PREFERENCE_FIELD_NUMBER: _ClassVar[int]
    dietary_preference: dietary_preference
    def __init__(self, dietary_preference: _Optional[_Union[dietary_preference, _Mapping]] = ...) -> None: ...

class UpdateDietaryPreference(_message.Message):
    __slots__ = ("store_uuid", "diet_pref_uuid", "name", "description", "icon_image_bytes")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    DIET_PREF_UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ICON_IMAGE_BYTES_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    diet_pref_uuid: str
    name: str
    description: str
    icon_image_bytes: bytes
    def __init__(self, store_uuid: _Optional[str] = ..., diet_pref_uuid: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., icon_image_bytes: _Optional[bytes] = ...) -> None: ...

class DeleteDietaryPreference(_message.Message):
    __slots__ = ("store_uuid", "diet_pref_uuid")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    DIET_PREF_UUID_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    diet_pref_uuid: str
    def __init__(self, store_uuid: _Optional[str] = ..., diet_pref_uuid: _Optional[str] = ...) -> None: ...

class ListDietaryPreference(_message.Message):
    __slots__ = ("store_uuid", "page", "limit")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    page: int
    limit: int
    def __init__(self, store_uuid: _Optional[str] = ..., page: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class ListDietPrefResponse(_message.Message):
    __slots__ = ("dietary_preferences", "next_page", "prev_page")
    DIETARY_PREFERENCES_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_FIELD_NUMBER: _ClassVar[int]
    PREV_PAGE_FIELD_NUMBER: _ClassVar[int]
    dietary_preferences: _containers.RepeatedCompositeFieldContainer[dietary_preference]
    next_page: int
    prev_page: int
    def __init__(self, dietary_preferences: _Optional[_Iterable[_Union[dietary_preference, _Mapping]]] = ..., next_page: _Optional[int] = ..., prev_page: _Optional[int] = ...) -> None: ...
