from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TemplateCategory(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MARKETING: _ClassVar[TemplateCategory]
    UTILITY: _ClassVar[TemplateCategory]
    AUTHENTICATION: _ClassVar[TemplateCategory]

class TemplateStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PENDING: _ClassVar[TemplateStatus]
    APPROVED: _ClassVar[TemplateStatus]
    REJECTED: _ClassVar[TemplateStatus]

class TemplateParameterFormat(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    POSITIONAL: _ClassVar[TemplateParameterFormat]
    NAMED: _ClassVar[TemplateParameterFormat]

class TemplateComponentType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    HEADER: _ClassVar[TemplateComponentType]
    BODY: _ClassVar[TemplateComponentType]
    FOOTER: _ClassVar[TemplateComponentType]

class TemplateParameterType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TEXT: _ClassVar[TemplateParameterType]
    CURRENCY: _ClassVar[TemplateParameterType]
    MEDIA: _ClassVar[TemplateParameterType]

class TemplateButtonType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    QUICK_REPLY: _ClassVar[TemplateButtonType]
    URL: _ClassVar[TemplateButtonType]
MARKETING: TemplateCategory
UTILITY: TemplateCategory
AUTHENTICATION: TemplateCategory
PENDING: TemplateStatus
APPROVED: TemplateStatus
REJECTED: TemplateStatus
POSITIONAL: TemplateParameterFormat
NAMED: TemplateParameterFormat
HEADER: TemplateComponentType
BODY: TemplateComponentType
FOOTER: TemplateComponentType
TEXT: TemplateParameterType
CURRENCY: TemplateParameterType
MEDIA: TemplateParameterType
QUICK_REPLY: TemplateButtonType
URL: TemplateButtonType

class Template(_message.Message):
    __slots__ = ("id", "name", "category", "status", "language", "parameter_format", "message_send_ttl_seconds", "whatsapp_template_id", "components", "buttons")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    PARAMETER_FORMAT_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_SEND_TTL_SECONDS_FIELD_NUMBER: _ClassVar[int]
    WHATSAPP_TEMPLATE_ID_FIELD_NUMBER: _ClassVar[int]
    COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    BUTTONS_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    category: TemplateCategory
    status: TemplateStatus
    language: str
    parameter_format: TemplateParameterFormat
    message_send_ttl_seconds: int
    whatsapp_template_id: str
    components: _containers.RepeatedCompositeFieldContainer[TemplateComponent]
    buttons: _containers.RepeatedCompositeFieldContainer[TemplateButton]
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., category: _Optional[_Union[TemplateCategory, str]] = ..., status: _Optional[_Union[TemplateStatus, str]] = ..., language: _Optional[str] = ..., parameter_format: _Optional[_Union[TemplateParameterFormat, str]] = ..., message_send_ttl_seconds: _Optional[int] = ..., whatsapp_template_id: _Optional[str] = ..., components: _Optional[_Iterable[_Union[TemplateComponent, _Mapping]]] = ..., buttons: _Optional[_Iterable[_Union[TemplateButton, _Mapping]]] = ...) -> None: ...

class TemplateComponent(_message.Message):
    __slots__ = ("name", "type", "text", "format", "parameters")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: TemplateComponentType
    text: str
    format: str
    parameters: _containers.RepeatedCompositeFieldContainer[TemplateParameter]
    def __init__(self, name: _Optional[str] = ..., type: _Optional[_Union[TemplateComponentType, str]] = ..., text: _Optional[str] = ..., format: _Optional[str] = ..., parameters: _Optional[_Iterable[_Union[TemplateParameter, _Mapping]]] = ...) -> None: ...

class TemplateParameter(_message.Message):
    __slots__ = ("name", "type", "text_value", "index")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TEXT_VALUE_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: TemplateParameterType
    text_value: str
    index: int
    def __init__(self, name: _Optional[str] = ..., type: _Optional[_Union[TemplateParameterType, str]] = ..., text_value: _Optional[str] = ..., index: _Optional[int] = ...) -> None: ...

class TemplateButton(_message.Message):
    __slots__ = ("type", "text", "url", "index")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    type: TemplateButtonType
    text: str
    url: str
    index: int
    def __init__(self, type: _Optional[_Union[TemplateButtonType, str]] = ..., text: _Optional[str] = ..., url: _Optional[str] = ..., index: _Optional[int] = ...) -> None: ...

class GetTemplateRequest(_message.Message):
    __slots__ = ("id", "name", "whatsapp_template_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    WHATSAPP_TEMPLATE_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    whatsapp_template_id: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., whatsapp_template_id: _Optional[str] = ...) -> None: ...

class GetTemplateResponse(_message.Message):
    __slots__ = ("template",)
    TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    template: Template
    def __init__(self, template: _Optional[_Union[Template, _Mapping]] = ...) -> None: ...

class ListTemplatesRequest(_message.Message):
    __slots__ = ("category", "status", "language", "parameter_format", "page", "limit")
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    PARAMETER_FORMAT_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    category: str
    status: str
    language: str
    parameter_format: str
    page: int
    limit: int
    def __init__(self, category: _Optional[str] = ..., status: _Optional[str] = ..., language: _Optional[str] = ..., parameter_format: _Optional[str] = ..., page: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class ListTemplatesResponse(_message.Message):
    __slots__ = ("templates", "next_page", "previous_page")
    TEMPLATES_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_PAGE_FIELD_NUMBER: _ClassVar[int]
    templates: _containers.RepeatedCompositeFieldContainer[Template]
    next_page: int
    previous_page: int
    def __init__(self, templates: _Optional[_Iterable[_Union[Template, _Mapping]]] = ..., next_page: _Optional[int] = ..., previous_page: _Optional[int] = ...) -> None: ...
