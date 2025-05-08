import annotations_pb2 as _annotations_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ORDERTYPE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ORDER_TYPE_UNSPECIFIED: _ClassVar[ORDERTYPE]
    ORDER_TYPE_DINE_IN: _ClassVar[ORDERTYPE]
    ORDER_TYPE_TAKE_AWAY: _ClassVar[ORDERTYPE]
    ORDER_TYPE_DRIVE_THRU: _ClassVar[ORDERTYPE]

class CARTSTATE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CART_STATE_UNSPECIFIED_STATE: _ClassVar[CARTSTATE]
    CART_STATE_ACTIVE: _ClassVar[CARTSTATE]
    CART_STATE_LOCKED: _ClassVar[CARTSTATE]
    CART_STATE_ABANDONED: _ClassVar[CARTSTATE]

class DISCOUNTTYPE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNSPCIFIED_DISCOUNT: _ClassVar[DISCOUNTTYPE]
    PERCENTAGE_DISCOUNT: _ClassVar[DISCOUNTTYPE]
    FIXED_DISCOUNT: _ClassVar[DISCOUNTTYPE]
ORDER_TYPE_UNSPECIFIED: ORDERTYPE
ORDER_TYPE_DINE_IN: ORDERTYPE
ORDER_TYPE_TAKE_AWAY: ORDERTYPE
ORDER_TYPE_DRIVE_THRU: ORDERTYPE
CART_STATE_UNSPECIFIED_STATE: CARTSTATE
CART_STATE_ACTIVE: CARTSTATE
CART_STATE_LOCKED: CARTSTATE
CART_STATE_ABANDONED: CARTSTATE
UNSPCIFIED_DISCOUNT: DISCOUNTTYPE
PERCENTAGE_DISCOUNT: DISCOUNTTYPE
FIXED_DISCOUNT: DISCOUNTTYPE

class Cart(_message.Message):
    __slots__ = ("store_uuid", "cart_uuid", "user_phone_no", "order_type", "table_no", "vehicle_no", "vehicle_description", "coupon_code", "special_instructions", "items", "sub_total", "total_discount", "total_price_before_tax", "total_tax", "packaging_cost", "final_amount", "cart_state", "created_at", "updated_at")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    CART_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    ORDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    TABLE_NO_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_NO_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    COUPON_CODE_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_INSTRUCTIONS_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    SUB_TOTAL_FIELD_NUMBER: _ClassVar[int]
    TOTAL_DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PRICE_BEFORE_TAX_FIELD_NUMBER: _ClassVar[int]
    TOTAL_TAX_FIELD_NUMBER: _ClassVar[int]
    PACKAGING_COST_FIELD_NUMBER: _ClassVar[int]
    FINAL_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    CART_STATE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    cart_uuid: str
    user_phone_no: str
    order_type: ORDERTYPE
    table_no: str
    vehicle_no: str
    vehicle_description: str
    coupon_code: str
    special_instructions: str
    items: _containers.RepeatedCompositeFieldContainer[CartItem]
    sub_total: float
    total_discount: float
    total_price_before_tax: float
    total_tax: float
    packaging_cost: float
    final_amount: float
    cart_state: CARTSTATE
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, store_uuid: _Optional[str] = ..., cart_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ..., order_type: _Optional[_Union[ORDERTYPE, str]] = ..., table_no: _Optional[str] = ..., vehicle_no: _Optional[str] = ..., vehicle_description: _Optional[str] = ..., coupon_code: _Optional[str] = ..., special_instructions: _Optional[str] = ..., items: _Optional[_Iterable[_Union[CartItem, _Mapping]]] = ..., sub_total: _Optional[float] = ..., total_discount: _Optional[float] = ..., total_price_before_tax: _Optional[float] = ..., total_tax: _Optional[float] = ..., packaging_cost: _Optional[float] = ..., final_amount: _Optional[float] = ..., cart_state: _Optional[_Union[CARTSTATE, str]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CartItem(_message.Message):
    __slots__ = ("cart_item_uuid", "cart_uuid", "product_name", "product_uuid", "tax_percentage", "discount", "unit_price", "quantity", "add_ons_total", "subtotal_amount", "discount_amount", "price_before_tax", "tax_amount", "final_price", "packaging_cost", "add_ons")
    CART_ITEM_UUID_FIELD_NUMBER: _ClassVar[int]
    CART_UUID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_NAME_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_UUID_FIELD_NUMBER: _ClassVar[int]
    TAX_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    ADD_ONS_TOTAL_FIELD_NUMBER: _ClassVar[int]
    SUBTOTAL_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    PRICE_BEFORE_TAX_FIELD_NUMBER: _ClassVar[int]
    TAX_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    FINAL_PRICE_FIELD_NUMBER: _ClassVar[int]
    PACKAGING_COST_FIELD_NUMBER: _ClassVar[int]
    ADD_ONS_FIELD_NUMBER: _ClassVar[int]
    cart_item_uuid: str
    cart_uuid: str
    product_name: str
    product_uuid: str
    tax_percentage: float
    discount: float
    unit_price: float
    quantity: int
    add_ons_total: float
    subtotal_amount: float
    discount_amount: float
    price_before_tax: float
    tax_amount: float
    final_price: float
    packaging_cost: float
    add_ons: _containers.RepeatedCompositeFieldContainer[AddOn]
    def __init__(self, cart_item_uuid: _Optional[str] = ..., cart_uuid: _Optional[str] = ..., product_name: _Optional[str] = ..., product_uuid: _Optional[str] = ..., tax_percentage: _Optional[float] = ..., discount: _Optional[float] = ..., unit_price: _Optional[float] = ..., quantity: _Optional[int] = ..., add_ons_total: _Optional[float] = ..., subtotal_amount: _Optional[float] = ..., discount_amount: _Optional[float] = ..., price_before_tax: _Optional[float] = ..., tax_amount: _Optional[float] = ..., final_price: _Optional[float] = ..., packaging_cost: _Optional[float] = ..., add_ons: _Optional[_Iterable[_Union[AddOn, _Mapping]]] = ...) -> None: ...

class AddOn(_message.Message):
    __slots__ = ("cart_item_uuid", "add_on_name", "add_on_uuid", "quantity", "unit_price", "is_free", "subtotal_amount")
    CART_ITEM_UUID_FIELD_NUMBER: _ClassVar[int]
    ADD_ON_NAME_FIELD_NUMBER: _ClassVar[int]
    ADD_ON_UUID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    IS_FREE_FIELD_NUMBER: _ClassVar[int]
    SUBTOTAL_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    cart_item_uuid: str
    add_on_name: str
    add_on_uuid: str
    quantity: int
    unit_price: float
    is_free: bool
    subtotal_amount: float
    def __init__(self, cart_item_uuid: _Optional[str] = ..., add_on_name: _Optional[str] = ..., add_on_uuid: _Optional[str] = ..., quantity: _Optional[int] = ..., unit_price: _Optional[float] = ..., is_free: bool = ..., subtotal_amount: _Optional[float] = ...) -> None: ...

class CreateCartRequest(_message.Message):
    __slots__ = ("store_uuid", "user_phone_no", "order_type", "table_no", "vehicle_no", "vehicle_description")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    ORDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    TABLE_NO_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_NO_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    user_phone_no: str
    order_type: ORDERTYPE
    table_no: str
    vehicle_no: str
    vehicle_description: str
    def __init__(self, store_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ..., order_type: _Optional[_Union[ORDERTYPE, str]] = ..., table_no: _Optional[str] = ..., vehicle_no: _Optional[str] = ..., vehicle_description: _Optional[str] = ...) -> None: ...

class CartResponse(_message.Message):
    __slots__ = ("cart",)
    CART_FIELD_NUMBER: _ClassVar[int]
    cart: Cart
    def __init__(self, cart: _Optional[_Union[Cart, _Mapping]] = ...) -> None: ...

class GetCartRequest(_message.Message):
    __slots__ = ("store_uuid", "user_phone_no", "cart_uuid")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    CART_UUID_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    user_phone_no: str
    cart_uuid: str
    def __init__(self, store_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ..., cart_uuid: _Optional[str] = ...) -> None: ...

class UpdateCartRequest(_message.Message):
    __slots__ = ("store_uuid", "user_phone_no", "cart_uuid", "order_type", "table_no", "vehicle_no", "vehicle_description", "coupon_code", "special_instructions")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    CART_UUID_FIELD_NUMBER: _ClassVar[int]
    ORDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    TABLE_NO_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_NO_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    COUPON_CODE_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_INSTRUCTIONS_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    user_phone_no: str
    cart_uuid: str
    order_type: ORDERTYPE
    table_no: str
    vehicle_no: str
    vehicle_description: str
    coupon_code: str
    special_instructions: str
    def __init__(self, store_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ..., cart_uuid: _Optional[str] = ..., order_type: _Optional[_Union[ORDERTYPE, str]] = ..., table_no: _Optional[str] = ..., vehicle_no: _Optional[str] = ..., vehicle_description: _Optional[str] = ..., coupon_code: _Optional[str] = ..., special_instructions: _Optional[str] = ...) -> None: ...

class DeleteCartRequest(_message.Message):
    __slots__ = ("store_uuid", "user_phone_no", "cart_uuid")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    CART_UUID_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    user_phone_no: str
    cart_uuid: str
    def __init__(self, store_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ..., cart_uuid: _Optional[str] = ...) -> None: ...

class AddCartItemRequest(_message.Message):
    __slots__ = ("cart_uuid", "store_uuid", "user_phone_no", "product_uuid")
    CART_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_UUID_FIELD_NUMBER: _ClassVar[int]
    cart_uuid: str
    store_uuid: str
    user_phone_no: str
    product_uuid: str
    def __init__(self, cart_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ..., product_uuid: _Optional[str] = ...) -> None: ...

class RemoveCartItemRequest(_message.Message):
    __slots__ = ("cart_uuid", "user_phone_no", "store_uuid", "cart_item_uuid", "product_uuid")
    CART_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    CART_ITEM_UUID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_UUID_FIELD_NUMBER: _ClassVar[int]
    cart_uuid: str
    user_phone_no: str
    store_uuid: str
    cart_item_uuid: str
    product_uuid: str
    def __init__(self, cart_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ..., store_uuid: _Optional[str] = ..., cart_item_uuid: _Optional[str] = ..., product_uuid: _Optional[str] = ...) -> None: ...

class AddQuantityRequest(_message.Message):
    __slots__ = ("cart_uuid", "cart_item_uuid", "product_uuid", "store_uuid", "user_phone_no")
    CART_UUID_FIELD_NUMBER: _ClassVar[int]
    CART_ITEM_UUID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    cart_uuid: str
    cart_item_uuid: str
    product_uuid: str
    store_uuid: str
    user_phone_no: str
    def __init__(self, cart_uuid: _Optional[str] = ..., cart_item_uuid: _Optional[str] = ..., product_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ...) -> None: ...

class RemoveQuantityRequest(_message.Message):
    __slots__ = ("cart_uuid", "cart_item_uuid", "product_uuid", "store_uuid", "user_phone_no")
    CART_UUID_FIELD_NUMBER: _ClassVar[int]
    CART_ITEM_UUID_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    cart_uuid: str
    cart_item_uuid: str
    product_uuid: str
    store_uuid: str
    user_phone_no: str
    def __init__(self, cart_uuid: _Optional[str] = ..., cart_item_uuid: _Optional[str] = ..., product_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ...) -> None: ...

class CreateAddOnRequest(_message.Message):
    __slots__ = ("cart_uuid", "cart_item_uuid", "add_on_uuid", "store_uuid", "user_phone_no")
    CART_UUID_FIELD_NUMBER: _ClassVar[int]
    CART_ITEM_UUID_FIELD_NUMBER: _ClassVar[int]
    ADD_ON_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    cart_uuid: str
    cart_item_uuid: str
    add_on_uuid: str
    store_uuid: str
    user_phone_no: str
    def __init__(self, cart_uuid: _Optional[str] = ..., cart_item_uuid: _Optional[str] = ..., add_on_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ...) -> None: ...

class RemoveAddOnRequest(_message.Message):
    __slots__ = ("cart_uuid", "cart_item_uuid", "add_on_uuid", "store_uuid", "user_phone_no")
    CART_UUID_FIELD_NUMBER: _ClassVar[int]
    CART_ITEM_UUID_FIELD_NUMBER: _ClassVar[int]
    ADD_ON_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    cart_uuid: str
    cart_item_uuid: str
    add_on_uuid: str
    store_uuid: str
    user_phone_no: str
    def __init__(self, cart_uuid: _Optional[str] = ..., cart_item_uuid: _Optional[str] = ..., add_on_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ...) -> None: ...

class IncreaseAddOnQuantityRequest(_message.Message):
    __slots__ = ("cart_uuid", "cart_item_uuid", "add_on_uuid", "store_uuid", "user_phone_no")
    CART_UUID_FIELD_NUMBER: _ClassVar[int]
    CART_ITEM_UUID_FIELD_NUMBER: _ClassVar[int]
    ADD_ON_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    cart_uuid: str
    cart_item_uuid: str
    add_on_uuid: str
    store_uuid: str
    user_phone_no: str
    def __init__(self, cart_uuid: _Optional[str] = ..., cart_item_uuid: _Optional[str] = ..., add_on_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ...) -> None: ...

class RemoveAddOnQuantityRequest(_message.Message):
    __slots__ = ("cart_uuid", "cart_item_uuid", "add_on_uuid", "store_uuid", "user_phone_no")
    CART_UUID_FIELD_NUMBER: _ClassVar[int]
    CART_ITEM_UUID_FIELD_NUMBER: _ClassVar[int]
    ADD_ON_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    cart_uuid: str
    cart_item_uuid: str
    add_on_uuid: str
    store_uuid: str
    user_phone_no: str
    def __init__(self, cart_uuid: _Optional[str] = ..., cart_item_uuid: _Optional[str] = ..., add_on_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ...) -> None: ...

class ValidCouponResquest(_message.Message):
    __slots__ = ("cart_uuid", "coupon_code", "store_uuid", "user_phone_no")
    CART_UUID_FIELD_NUMBER: _ClassVar[int]
    COUPON_CODE_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    cart_uuid: str
    coupon_code: str
    store_uuid: str
    user_phone_no: str
    def __init__(self, cart_uuid: _Optional[str] = ..., coupon_code: _Optional[str] = ..., store_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ...) -> None: ...

class ValidCouponResponse(_message.Message):
    __slots__ = ("valid", "message")
    VALID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    valid: bool
    message: str
    def __init__(self, valid: bool = ..., message: _Optional[str] = ...) -> None: ...

class AddCouponRequest(_message.Message):
    __slots__ = ("cart_uuid", "coupon_code", "store_uuid", "user_phone_no")
    CART_UUID_FIELD_NUMBER: _ClassVar[int]
    COUPON_CODE_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    cart_uuid: str
    coupon_code: str
    store_uuid: str
    user_phone_no: str
    def __init__(self, cart_uuid: _Optional[str] = ..., coupon_code: _Optional[str] = ..., store_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ...) -> None: ...

class RemoveCouponRequest(_message.Message):
    __slots__ = ("cart_uuid", "store_uuid", "user_phone_no")
    CART_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    cart_uuid: str
    store_uuid: str
    user_phone_no: str
    def __init__(self, cart_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ...) -> None: ...

class ValidateCartRequest(_message.Message):
    __slots__ = ("cart_uuid", "store_uuid", "user_phone_no")
    CART_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    cart_uuid: str
    store_uuid: str
    user_phone_no: str
    def __init__(self, cart_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ...) -> None: ...

class Coupon(_message.Message):
    __slots__ = ("coupon_uuid", "store_uuid", "coupon_code", "discount_type", "valid_from", "valid_to", "usage_limit_per_user", "total_usage_limit", "discount", "min_spend", "is_for_new_users", "description", "max_cart_value", "is_active", "max_discount")
    COUPON_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    COUPON_CODE_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_TYPE_FIELD_NUMBER: _ClassVar[int]
    VALID_FROM_FIELD_NUMBER: _ClassVar[int]
    VALID_TO_FIELD_NUMBER: _ClassVar[int]
    USAGE_LIMIT_PER_USER_FIELD_NUMBER: _ClassVar[int]
    TOTAL_USAGE_LIMIT_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    MIN_SPEND_FIELD_NUMBER: _ClassVar[int]
    IS_FOR_NEW_USERS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MAX_CART_VALUE_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    MAX_DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    coupon_uuid: str
    store_uuid: str
    coupon_code: str
    discount_type: DISCOUNTTYPE
    valid_from: _timestamp_pb2.Timestamp
    valid_to: _timestamp_pb2.Timestamp
    usage_limit_per_user: int
    total_usage_limit: int
    discount: float
    min_spend: float
    is_for_new_users: bool
    description: str
    max_cart_value: float
    is_active: bool
    max_discount: float
    def __init__(self, coupon_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., coupon_code: _Optional[str] = ..., discount_type: _Optional[_Union[DISCOUNTTYPE, str]] = ..., valid_from: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., valid_to: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., usage_limit_per_user: _Optional[int] = ..., total_usage_limit: _Optional[int] = ..., discount: _Optional[float] = ..., min_spend: _Optional[float] = ..., is_for_new_users: bool = ..., description: _Optional[str] = ..., max_cart_value: _Optional[float] = ..., is_active: bool = ..., max_discount: _Optional[float] = ...) -> None: ...

class CouponUsage(_message.Message):
    __slots__ = ("usage_uuid", "coupon_uuid", "user_phone_no", "used_at", "order_uuid")
    USAGE_UUID_FIELD_NUMBER: _ClassVar[int]
    COUPON_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    USED_AT_FIELD_NUMBER: _ClassVar[int]
    ORDER_UUID_FIELD_NUMBER: _ClassVar[int]
    usage_uuid: str
    coupon_uuid: str
    user_phone_no: str
    used_at: _timestamp_pb2.Timestamp
    order_uuid: str
    def __init__(self, usage_uuid: _Optional[str] = ..., coupon_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ..., used_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., order_uuid: _Optional[str] = ...) -> None: ...

class CreateCouponRequest(_message.Message):
    __slots__ = ("store_uuid", "coupon")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    COUPON_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    coupon: Coupon
    def __init__(self, store_uuid: _Optional[str] = ..., coupon: _Optional[_Union[Coupon, _Mapping]] = ...) -> None: ...

class GetCouponRequest(_message.Message):
    __slots__ = ("store_uuid", "coupon_uuid", "coupon_code")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    COUPON_UUID_FIELD_NUMBER: _ClassVar[int]
    COUPON_CODE_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    coupon_uuid: str
    coupon_code: str
    def __init__(self, store_uuid: _Optional[str] = ..., coupon_uuid: _Optional[str] = ..., coupon_code: _Optional[str] = ...) -> None: ...

class UpdateCouponRequest(_message.Message):
    __slots__ = ("store_uuid", "coupon_uuid", "coupon_code", "discount_type", "valid_from", "valid_to", "usage_limit_per_user", "total_usage_limit", "discount", "min_spend", "is_for_new_users", "description", "max_cart_value", "is_active", "max_discount")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    COUPON_UUID_FIELD_NUMBER: _ClassVar[int]
    COUPON_CODE_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_TYPE_FIELD_NUMBER: _ClassVar[int]
    VALID_FROM_FIELD_NUMBER: _ClassVar[int]
    VALID_TO_FIELD_NUMBER: _ClassVar[int]
    USAGE_LIMIT_PER_USER_FIELD_NUMBER: _ClassVar[int]
    TOTAL_USAGE_LIMIT_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    MIN_SPEND_FIELD_NUMBER: _ClassVar[int]
    IS_FOR_NEW_USERS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MAX_CART_VALUE_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    MAX_DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    coupon_uuid: str
    coupon_code: str
    discount_type: DISCOUNTTYPE
    valid_from: _timestamp_pb2.Timestamp
    valid_to: _timestamp_pb2.Timestamp
    usage_limit_per_user: int
    total_usage_limit: int
    discount: float
    min_spend: float
    is_for_new_users: bool
    description: str
    max_cart_value: float
    is_active: bool
    max_discount: float
    def __init__(self, store_uuid: _Optional[str] = ..., coupon_uuid: _Optional[str] = ..., coupon_code: _Optional[str] = ..., discount_type: _Optional[_Union[DISCOUNTTYPE, str]] = ..., valid_from: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., valid_to: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., usage_limit_per_user: _Optional[int] = ..., total_usage_limit: _Optional[int] = ..., discount: _Optional[float] = ..., min_spend: _Optional[float] = ..., is_for_new_users: bool = ..., description: _Optional[str] = ..., max_cart_value: _Optional[float] = ..., is_active: bool = ..., max_discount: _Optional[float] = ...) -> None: ...

class DeleteCouponRequest(_message.Message):
    __slots__ = ("store_uuid", "coupon_uuid")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    COUPON_UUID_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    coupon_uuid: str
    def __init__(self, store_uuid: _Optional[str] = ..., coupon_uuid: _Optional[str] = ...) -> None: ...

class listCouponRequest(_message.Message):
    __slots__ = ("store_uuid", "page", "limit")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    page: int
    limit: int
    def __init__(self, store_uuid: _Optional[str] = ..., page: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class listCouponResponse(_message.Message):
    __slots__ = ("coupons", "next_page", "prev_page")
    COUPONS_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_FIELD_NUMBER: _ClassVar[int]
    PREV_PAGE_FIELD_NUMBER: _ClassVar[int]
    coupons: _containers.RepeatedCompositeFieldContainer[Coupon]
    next_page: int
    prev_page: int
    def __init__(self, coupons: _Optional[_Iterable[_Union[Coupon, _Mapping]]] = ..., next_page: _Optional[int] = ..., prev_page: _Optional[int] = ...) -> None: ...

class GetCouponUsageRequest(_message.Message):
    __slots__ = ("store_uuid", "coupon_uuid", "page", "limit")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    COUPON_UUID_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    coupon_uuid: str
    page: int
    limit: int
    def __init__(self, store_uuid: _Optional[str] = ..., coupon_uuid: _Optional[str] = ..., page: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class GetCouponUsageResponse(_message.Message):
    __slots__ = ("coupon_usage_list", "next_page", "prev_page")
    COUPON_USAGE_LIST_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_FIELD_NUMBER: _ClassVar[int]
    PREV_PAGE_FIELD_NUMBER: _ClassVar[int]
    coupon_usage_list: _containers.RepeatedCompositeFieldContainer[CouponUsage]
    next_page: int
    prev_page: int
    def __init__(self, coupon_usage_list: _Optional[_Iterable[_Union[CouponUsage, _Mapping]]] = ..., next_page: _Optional[int] = ..., prev_page: _Optional[int] = ...) -> None: ...
