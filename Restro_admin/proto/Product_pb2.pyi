from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateProductRequest(_message.Message):
    __slots__ = ("StoreUuid", "Name", "IsAvailable", "Price", "CategoryUuid", "Description", "ImageUrl")
    STOREUUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ISAVAILABLE_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    CATEGORYUUID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IMAGEURL_FIELD_NUMBER: _ClassVar[int]
    StoreUuid: str
    Name: str
    IsAvailable: bool
    Price: float
    CategoryUuid: str
    Description: str
    ImageUrl: str
    def __init__(self, StoreUuid: _Optional[str] = ..., Name: _Optional[str] = ..., IsAvailable: bool = ..., Price: _Optional[float] = ..., CategoryUuid: _Optional[str] = ..., Description: _Optional[str] = ..., ImageUrl: _Optional[str] = ...) -> None: ...

class GetProductRequest(_message.Message):
    __slots__ = ("ProductUuid", "StoreUuid")
    PRODUCTUUID_FIELD_NUMBER: _ClassVar[int]
    STOREUUID_FIELD_NUMBER: _ClassVar[int]
    ProductUuid: str
    StoreUuid: str
    def __init__(self, ProductUuid: _Optional[str] = ..., StoreUuid: _Optional[str] = ...) -> None: ...

class ListProductsRequest(_message.Message):
    __slots__ = ("StoreUuid",)
    STOREUUID_FIELD_NUMBER: _ClassVar[int]
    StoreUuid: str
    def __init__(self, StoreUuid: _Optional[str] = ...) -> None: ...

class DeleteProductRequest(_message.Message):
    __slots__ = ("ProductUuid",)
    PRODUCTUUID_FIELD_NUMBER: _ClassVar[int]
    ProductUuid: str
    def __init__(self, ProductUuid: _Optional[str] = ...) -> None: ...

class UpdateProductRequest(_message.Message):
    __slots__ = ("ProductUuid", "Name", "IsAvailable", "Price", "CategoryUuid", "Description", "ImageUrl")
    PRODUCTUUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ISAVAILABLE_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    CATEGORYUUID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IMAGEURL_FIELD_NUMBER: _ClassVar[int]
    ProductUuid: str
    Name: str
    IsAvailable: bool
    Price: float
    CategoryUuid: str
    Description: str
    ImageUrl: str
    def __init__(self, ProductUuid: _Optional[str] = ..., Name: _Optional[str] = ..., IsAvailable: bool = ..., Price: _Optional[float] = ..., CategoryUuid: _Optional[str] = ..., Description: _Optional[str] = ..., ImageUrl: _Optional[str] = ...) -> None: ...

class ProductResponse(_message.Message):
    __slots__ = ("Success", "ProductUuid", "Name", "IsAvailable", "Price", "CategoryUuid", "Description", "ImageUrl")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    PRODUCTUUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ISAVAILABLE_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    CATEGORYUUID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IMAGEURL_FIELD_NUMBER: _ClassVar[int]
    Success: bool
    ProductUuid: str
    Name: str
    IsAvailable: bool
    Price: float
    CategoryUuid: str
    Description: str
    ImageUrl: str
    def __init__(self, Success: bool = ..., ProductUuid: _Optional[str] = ..., Name: _Optional[str] = ..., IsAvailable: bool = ..., Price: _Optional[float] = ..., CategoryUuid: _Optional[str] = ..., Description: _Optional[str] = ..., ImageUrl: _Optional[str] = ...) -> None: ...

class DeleteProductResponse(_message.Message):
    __slots__ = ("Success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    Success: bool
    def __init__(self, Success: bool = ...) -> None: ...

class ListProductsResponse(_message.Message):
    __slots__ = ("products",)
    PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    products: _containers.RepeatedCompositeFieldContainer[ProductResponse]
    def __init__(self, products: _Optional[_Iterable[_Union[ProductResponse, _Mapping]]] = ...) -> None: ...
