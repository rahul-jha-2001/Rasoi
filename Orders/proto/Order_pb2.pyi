from google.protobuf import timestamp_pb2 as _timestamp_pb2
import annotations_pb2 as _annotations_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OrderState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ORDER_STATE_UNSPECIFIED: _ClassVar[OrderState]
    ORDER_STATE_PAYMENT_PENDING: _ClassVar[OrderState]
    ORDER_STATE_PLACED: _ClassVar[OrderState]
    ORDER_STATE_PREPARING: _ClassVar[OrderState]
    ORDER_STATE_READY: _ClassVar[OrderState]
    ORDER_STATE_COMPLETED: _ClassVar[OrderState]
    ORDER_STATE_CANCELED: _ClassVar[OrderState]

class PaymentState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PAYMENT_STATE_UNSPECIFIED: _ClassVar[PaymentState]
    PAYMENT_STATE_PENDING: _ClassVar[PaymentState]
    PAYMENT_STATE_COMPLETE: _ClassVar[PaymentState]
    PAYMENT_STATE_FAILED: _ClassVar[PaymentState]
    PAYMENT_STATE_REFUNDED: _ClassVar[PaymentState]

class PaymentMethod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PAYMENT_METHOD_UNSPECIFIED: _ClassVar[PaymentMethod]
    PAYMENT_METHOD_RAZORPAY: _ClassVar[PaymentMethod]
    PAYMENT_METHOD_CASH: _ClassVar[PaymentMethod]
    PAYMENT_METHOD_CARD: _ClassVar[PaymentMethod]
    PAYMENT_METHOD_UPI: _ClassVar[PaymentMethod]
    PAYMENT_METHOD_NETBANKING: _ClassVar[PaymentMethod]

class OrderType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ORDER_TYPE_UNSPECIFIED: _ClassVar[OrderType]
    ORDER_TYPE_DINE_IN: _ClassVar[OrderType]
    ORDER_TYPE_TAKE_AWAY: _ClassVar[OrderType]
    ORDER_TYPE_DRIVE_THRU: _ClassVar[OrderType]
ORDER_STATE_UNSPECIFIED: OrderState
ORDER_STATE_PAYMENT_PENDING: OrderState
ORDER_STATE_PLACED: OrderState
ORDER_STATE_PREPARING: OrderState
ORDER_STATE_READY: OrderState
ORDER_STATE_COMPLETED: OrderState
ORDER_STATE_CANCELED: OrderState
PAYMENT_STATE_UNSPECIFIED: PaymentState
PAYMENT_STATE_PENDING: PaymentState
PAYMENT_STATE_COMPLETE: PaymentState
PAYMENT_STATE_FAILED: PaymentState
PAYMENT_STATE_REFUNDED: PaymentState
PAYMENT_METHOD_UNSPECIFIED: PaymentMethod
PAYMENT_METHOD_RAZORPAY: PaymentMethod
PAYMENT_METHOD_CASH: PaymentMethod
PAYMENT_METHOD_CARD: PaymentMethod
PAYMENT_METHOD_UPI: PaymentMethod
PAYMENT_METHOD_NETBANKING: PaymentMethod
ORDER_TYPE_UNSPECIFIED: OrderType
ORDER_TYPE_DINE_IN: OrderType
ORDER_TYPE_TAKE_AWAY: OrderType
ORDER_TYPE_DRIVE_THRU: OrderType

class OrderStoreView(_message.Message):
    __slots__ = ("order_uuid", "order_no", "store_uuid", "user_phone_no", "order_type", "table_no", "vehicle_no", "vehicle_description", "coupon_code", "items", "special_instructions", "order_status", "payment", "subtotal_amount", "discount_amount", "price_before_tax", "tax_amount", "packaging_cost", "final_amount", "created_at", "updated_at", "cart_uuid")
    ORDER_UUID_FIELD_NUMBER: _ClassVar[int]
    ORDER_NO_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    ORDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    TABLE_NO_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_NO_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    COUPON_CODE_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_INSTRUCTIONS_FIELD_NUMBER: _ClassVar[int]
    ORDER_STATUS_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_FIELD_NUMBER: _ClassVar[int]
    SUBTOTAL_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    PRICE_BEFORE_TAX_FIELD_NUMBER: _ClassVar[int]
    TAX_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    PACKAGING_COST_FIELD_NUMBER: _ClassVar[int]
    FINAL_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    CART_UUID_FIELD_NUMBER: _ClassVar[int]
    order_uuid: str
    order_no: str
    store_uuid: str
    user_phone_no: str
    order_type: OrderType
    table_no: str
    vehicle_no: str
    vehicle_description: str
    coupon_code: str
    items: _containers.RepeatedCompositeFieldContainer[OrderItem]
    special_instructions: str
    order_status: OrderState
    payment: OrderPayment
    subtotal_amount: float
    discount_amount: float
    price_before_tax: float
    tax_amount: float
    packaging_cost: float
    final_amount: float
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    cart_uuid: str
    def __init__(self, order_uuid: _Optional[str] = ..., order_no: _Optional[str] = ..., store_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ..., order_type: _Optional[_Union[OrderType, str]] = ..., table_no: _Optional[str] = ..., vehicle_no: _Optional[str] = ..., vehicle_description: _Optional[str] = ..., coupon_code: _Optional[str] = ..., items: _Optional[_Iterable[_Union[OrderItem, _Mapping]]] = ..., special_instructions: _Optional[str] = ..., order_status: _Optional[_Union[OrderState, str]] = ..., payment: _Optional[_Union[OrderPayment, _Mapping]] = ..., subtotal_amount: _Optional[float] = ..., discount_amount: _Optional[float] = ..., price_before_tax: _Optional[float] = ..., tax_amount: _Optional[float] = ..., packaging_cost: _Optional[float] = ..., final_amount: _Optional[float] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., cart_uuid: _Optional[str] = ...) -> None: ...

class OrderUserView(_message.Message):
    __slots__ = ("order_uuid", "order_no", "store_uuid", "cart_uuid", "user_phone_no", "order_type", "table_no", "vehicle_no", "vehicle_description", "coupon_code", "special_instructions", "order_status", "payment_method", "payment_state", "items", "total_subtotal", "total_discount", "total_price_before_tax", "total_tax", "packaging_cost", "final_amount", "created_at", "updated_at")
    ORDER_UUID_FIELD_NUMBER: _ClassVar[int]
    ORDER_NO_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    CART_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    ORDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    TABLE_NO_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_NO_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    COUPON_CODE_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_INSTRUCTIONS_FIELD_NUMBER: _ClassVar[int]
    ORDER_STATUS_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_METHOD_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_STATE_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SUBTOTAL_FIELD_NUMBER: _ClassVar[int]
    TOTAL_DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PRICE_BEFORE_TAX_FIELD_NUMBER: _ClassVar[int]
    TOTAL_TAX_FIELD_NUMBER: _ClassVar[int]
    PACKAGING_COST_FIELD_NUMBER: _ClassVar[int]
    FINAL_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    order_uuid: str
    order_no: str
    store_uuid: str
    cart_uuid: str
    user_phone_no: str
    order_type: OrderType
    table_no: str
    vehicle_no: str
    vehicle_description: str
    coupon_code: str
    special_instructions: str
    order_status: OrderState
    payment_method: PaymentMethod
    payment_state: PaymentState
    items: _containers.RepeatedCompositeFieldContainer[OrderItem]
    total_subtotal: float
    total_discount: float
    total_price_before_tax: float
    total_tax: float
    packaging_cost: float
    final_amount: float
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, order_uuid: _Optional[str] = ..., order_no: _Optional[str] = ..., store_uuid: _Optional[str] = ..., cart_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ..., order_type: _Optional[_Union[OrderType, str]] = ..., table_no: _Optional[str] = ..., vehicle_no: _Optional[str] = ..., vehicle_description: _Optional[str] = ..., coupon_code: _Optional[str] = ..., special_instructions: _Optional[str] = ..., order_status: _Optional[_Union[OrderState, str]] = ..., payment_method: _Optional[_Union[PaymentMethod, str]] = ..., payment_state: _Optional[_Union[PaymentState, str]] = ..., items: _Optional[_Iterable[_Union[OrderItem, _Mapping]]] = ..., total_subtotal: _Optional[float] = ..., total_discount: _Optional[float] = ..., total_price_before_tax: _Optional[float] = ..., total_tax: _Optional[float] = ..., packaging_cost: _Optional[float] = ..., final_amount: _Optional[float] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class OrderItem(_message.Message):
    __slots__ = ("item_uuid", "product_name", "product_uuid", "tax_percentage", "discount", "unit_price", "quantity", "add_ons_total", "subtotal_amount", "discount_amount", "price_before_tax", "tax_amount", "final_price", "packaging_cost", "add_ons")
    ITEM_UUID_FIELD_NUMBER: _ClassVar[int]
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
    item_uuid: str
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
    add_ons: _containers.RepeatedCompositeFieldContainer[OrderItemAddOn]
    def __init__(self, item_uuid: _Optional[str] = ..., product_name: _Optional[str] = ..., product_uuid: _Optional[str] = ..., tax_percentage: _Optional[float] = ..., discount: _Optional[float] = ..., unit_price: _Optional[float] = ..., quantity: _Optional[int] = ..., add_ons_total: _Optional[float] = ..., subtotal_amount: _Optional[float] = ..., discount_amount: _Optional[float] = ..., price_before_tax: _Optional[float] = ..., tax_amount: _Optional[float] = ..., final_price: _Optional[float] = ..., packaging_cost: _Optional[float] = ..., add_ons: _Optional[_Iterable[_Union[OrderItemAddOn, _Mapping]]] = ...) -> None: ...

class OrderItemAddOn(_message.Message):
    __slots__ = ("add_on_name", "add_on_uuid", "quantity", "unit_price", "is_free", "subtotal_amount")
    ADD_ON_NAME_FIELD_NUMBER: _ClassVar[int]
    ADD_ON_UUID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    IS_FREE_FIELD_NUMBER: _ClassVar[int]
    SUBTOTAL_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    add_on_name: str
    add_on_uuid: str
    quantity: int
    unit_price: float
    is_free: bool
    subtotal_amount: float
    def __init__(self, add_on_name: _Optional[str] = ..., add_on_uuid: _Optional[str] = ..., quantity: _Optional[int] = ..., unit_price: _Optional[float] = ..., is_free: bool = ..., subtotal_amount: _Optional[float] = ...) -> None: ...

class OrderPayment(_message.Message):
    __slots__ = ("payment_uuid", "rz_order_id", "rz_payment_id", "rz_signature", "amount", "payment_status", "payment_method", "notes", "payment_time")
    PAYMENT_UUID_FIELD_NUMBER: _ClassVar[int]
    RZ_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    RZ_PAYMENT_ID_FIELD_NUMBER: _ClassVar[int]
    RZ_SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_STATUS_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_METHOD_FIELD_NUMBER: _ClassVar[int]
    NOTES_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_TIME_FIELD_NUMBER: _ClassVar[int]
    payment_uuid: str
    rz_order_id: str
    rz_payment_id: str
    rz_signature: str
    amount: float
    payment_status: PaymentState
    payment_method: PaymentMethod
    notes: str
    payment_time: _timestamp_pb2.Timestamp
    def __init__(self, payment_uuid: _Optional[str] = ..., rz_order_id: _Optional[str] = ..., rz_payment_id: _Optional[str] = ..., rz_signature: _Optional[str] = ..., amount: _Optional[float] = ..., payment_status: _Optional[_Union[PaymentState, str]] = ..., payment_method: _Optional[_Union[PaymentMethod, str]] = ..., notes: _Optional[str] = ..., payment_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CreateOrderRequest(_message.Message):
    __slots__ = ("store_uuid", "user_phone_no", "cart_uuid")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    CART_UUID_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    user_phone_no: str
    cart_uuid: str
    def __init__(self, store_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ..., cart_uuid: _Optional[str] = ...) -> None: ...

class GetUserOrderRequest(_message.Message):
    __slots__ = ("order_uuid", "store_uuid", "user_phone_no", "order_no")
    ORDER_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    ORDER_NO_FIELD_NUMBER: _ClassVar[int]
    order_uuid: str
    store_uuid: str
    user_phone_no: str
    order_no: str
    def __init__(self, order_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ..., order_no: _Optional[str] = ...) -> None: ...

class CancelOrderRequest(_message.Message):
    __slots__ = ("store_uuid", "user_phone_no", "order_uuid", "order_no")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    ORDER_UUID_FIELD_NUMBER: _ClassVar[int]
    ORDER_NO_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    user_phone_no: str
    order_uuid: str
    order_no: str
    def __init__(self, store_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ..., order_uuid: _Optional[str] = ..., order_no: _Optional[str] = ...) -> None: ...

class ListStoreOrderRequest(_message.Message):
    __slots__ = ("store_uuid", "user_phone_no", "limit", "page")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    user_phone_no: str
    limit: int
    page: int
    def __init__(self, store_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ..., limit: _Optional[int] = ..., page: _Optional[int] = ...) -> None: ...

class StreamOrderRequest(_message.Message):
    __slots__ = ("store_uuid",)
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    def __init__(self, store_uuid: _Optional[str] = ...) -> None: ...

class ListStoreOrderResponse(_message.Message):
    __slots__ = ("orders", "next_page", "prev_page")
    ORDERS_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_FIELD_NUMBER: _ClassVar[int]
    PREV_PAGE_FIELD_NUMBER: _ClassVar[int]
    orders: _containers.RepeatedCompositeFieldContainer[OrderStoreView]
    next_page: int
    prev_page: int
    def __init__(self, orders: _Optional[_Iterable[_Union[OrderStoreView, _Mapping]]] = ..., next_page: _Optional[int] = ..., prev_page: _Optional[int] = ...) -> None: ...

class UserOrderResponse(_message.Message):
    __slots__ = ("order",)
    ORDER_FIELD_NUMBER: _ClassVar[int]
    order: OrderUserView
    def __init__(self, order: _Optional[_Union[OrderUserView, _Mapping]] = ...) -> None: ...

class StoreOrderResponse(_message.Message):
    __slots__ = ("order",)
    ORDER_FIELD_NUMBER: _ClassVar[int]
    order: OrderStoreView
    def __init__(self, order: _Optional[_Union[OrderStoreView, _Mapping]] = ...) -> None: ...

class ListUserOrderRequest(_message.Message):
    __slots__ = ("store_uuid", "user_phone_no", "limit", "page")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    user_phone_no: str
    limit: int
    page: int
    def __init__(self, store_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ..., limit: _Optional[int] = ..., page: _Optional[int] = ...) -> None: ...

class ListUserOrderResponse(_message.Message):
    __slots__ = ("orders", "next_page", "prev_page")
    ORDERS_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_FIELD_NUMBER: _ClassVar[int]
    PREV_PAGE_FIELD_NUMBER: _ClassVar[int]
    orders: _containers.RepeatedCompositeFieldContainer[OrderUserView]
    next_page: int
    prev_page: int
    def __init__(self, orders: _Optional[_Iterable[_Union[OrderUserView, _Mapping]]] = ..., next_page: _Optional[int] = ..., prev_page: _Optional[int] = ...) -> None: ...

class OrderResponse(_message.Message):
    __slots__ = ("order",)
    ORDER_FIELD_NUMBER: _ClassVar[int]
    order: OrderStoreView
    def __init__(self, order: _Optional[_Union[OrderStoreView, _Mapping]] = ...) -> None: ...

class GetOrderRequest(_message.Message):
    __slots__ = ("order_uuid", "store_uuid", "user_phone_no", "order_no")
    ORDER_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    ORDER_NO_FIELD_NUMBER: _ClassVar[int]
    order_uuid: str
    store_uuid: str
    user_phone_no: str
    order_no: str
    def __init__(self, order_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ..., order_no: _Optional[str] = ...) -> None: ...

class UpdateOrderStateRequest(_message.Message):
    __slots__ = ("order_uuid", "store_uuid", "order_state")
    ORDER_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    ORDER_STATE_FIELD_NUMBER: _ClassVar[int]
    order_uuid: str
    store_uuid: str
    order_state: OrderState
    def __init__(self, order_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., order_state: _Optional[_Union[OrderState, str]] = ...) -> None: ...

class DeleteOrderRequest(_message.Message):
    __slots__ = ("order_uuid", "store_uuid", "user_phone_no", "order_no")
    ORDER_UUID_FIELD_NUMBER: _ClassVar[int]
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    ORDER_NO_FIELD_NUMBER: _ClassVar[int]
    order_uuid: str
    store_uuid: str
    user_phone_no: str
    order_no: str
    def __init__(self, order_uuid: _Optional[str] = ..., store_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ..., order_no: _Optional[str] = ...) -> None: ...

class CancelUserOrderRequest(_message.Message):
    __slots__ = ("store_uuid", "user_phone_no", "order_no", "order_uuid")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    ORDER_NO_FIELD_NUMBER: _ClassVar[int]
    ORDER_UUID_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    user_phone_no: str
    order_no: str
    order_uuid: str
    def __init__(self, store_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ..., order_no: _Optional[str] = ..., order_uuid: _Optional[str] = ...) -> None: ...

class ListOrderRequest(_message.Message):
    __slots__ = ("store_uuid", "user_phone_no", "limit", "page")
    STORE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_PHONE_NO_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    PAGE_FIELD_NUMBER: _ClassVar[int]
    store_uuid: str
    user_phone_no: str
    limit: int
    page: int
    def __init__(self, store_uuid: _Optional[str] = ..., user_phone_no: _Optional[str] = ..., limit: _Optional[int] = ..., page: _Optional[int] = ...) -> None: ...

class ListOrderResponse(_message.Message):
    __slots__ = ("orders", "next_page", "prev_page")
    ORDERS_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_FIELD_NUMBER: _ClassVar[int]
    PREV_PAGE_FIELD_NUMBER: _ClassVar[int]
    orders: _containers.RepeatedCompositeFieldContainer[OrderStoreView]
    next_page: int
    prev_page: int
    def __init__(self, orders: _Optional[_Iterable[_Union[OrderStoreView, _Mapping]]] = ..., next_page: _Optional[int] = ..., prev_page: _Optional[int] = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
