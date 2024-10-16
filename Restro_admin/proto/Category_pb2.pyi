from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateCategoryRequest(_message.Message):
    __slots__ = ("StoreUuid", "Name", "Description", "ParentCategoryUuid")
    STOREUUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PARENTCATEGORYUUID_FIELD_NUMBER: _ClassVar[int]
    StoreUuid: str
    Name: str
    Description: str
    ParentCategoryUuid: str
    def __init__(self, StoreUuid: _Optional[str] = ..., Name: _Optional[str] = ..., Description: _Optional[str] = ..., ParentCategoryUuid: _Optional[str] = ...) -> None: ...

class GetCategoryRequest(_message.Message):
    __slots__ = ("CategoryUuid",)
    CATEGORYUUID_FIELD_NUMBER: _ClassVar[int]
    CategoryUuid: str
    def __init__(self, CategoryUuid: _Optional[str] = ...) -> None: ...

class UpdateCategoryRequest(_message.Message):
    __slots__ = ("CategoryUuid", "Name", "Description", "ParentCategoryUuid")
    CATEGORYUUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PARENTCATEGORYUUID_FIELD_NUMBER: _ClassVar[int]
    CategoryUuid: str
    Name: str
    Description: str
    ParentCategoryUuid: str
    def __init__(self, CategoryUuid: _Optional[str] = ..., Name: _Optional[str] = ..., Description: _Optional[str] = ..., ParentCategoryUuid: _Optional[str] = ...) -> None: ...

class DeleteCategoryRequest(_message.Message):
    __slots__ = ("CategoryUuid",)
    CATEGORYUUID_FIELD_NUMBER: _ClassVar[int]
    CategoryUuid: str
    def __init__(self, CategoryUuid: _Optional[str] = ...) -> None: ...

class ListCategoriesRequest(_message.Message):
    __slots__ = ("StoreUuid",)
    STOREUUID_FIELD_NUMBER: _ClassVar[int]
    StoreUuid: str
    def __init__(self, StoreUuid: _Optional[str] = ...) -> None: ...

class CategoryResponse(_message.Message):
    __slots__ = ("Success", "CategoryUuid", "Name", "Description", "ParentCategoryUuid")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    CATEGORYUUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PARENTCATEGORYUUID_FIELD_NUMBER: _ClassVar[int]
    Success: bool
    CategoryUuid: str
    Name: str
    Description: str
    ParentCategoryUuid: str
    def __init__(self, Success: bool = ..., CategoryUuid: _Optional[str] = ..., Name: _Optional[str] = ..., Description: _Optional[str] = ..., ParentCategoryUuid: _Optional[str] = ...) -> None: ...

class ListCategoriesResponse(_message.Message):
    __slots__ = ("categories",)
    CATEGORIES_FIELD_NUMBER: _ClassVar[int]
    categories: _containers.RepeatedCompositeFieldContainer[CategoryResponse]
    def __init__(self, categories: _Optional[_Iterable[_Union[CategoryResponse, _Mapping]]] = ...) -> None: ...

class DeleteCategoryResponse(_message.Message):
    __slots__ = ("Success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    Success: bool
    def __init__(self, Success: bool = ...) -> None: ...
