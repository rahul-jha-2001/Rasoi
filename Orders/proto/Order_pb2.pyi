from google.protobuf import timestamp_pb2 as _timestamp_pb2
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
    ORDER_STATE_COMPLETE: _ClassVar[OrderState]
    ORDER_STATE_CANCELED: _ClassVar[OrderState]
    ORDER_STATE_PLACED: _ClassVar[OrderState]

class PaymentState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PAYMENT_STATE_UNSPECIFIED: _ClassVar[PaymentState]
    PAYMENT_STATE_COMPLETE: _ClassVar[PaymentState]
    PAYMENT_STATE_FAILED: _ClassVar[PaymentState]
    PAYMENT_STATE_PENDING: _ClassVar[PaymentState]

class OrderType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ORDER_TYPE_UNSPECIFIED: _ClassVar[OrderType]
    ORDER_TYPE_DINE_IN: _ClassVar[OrderType]
    ORDER_TYPE_TAKE_AWAY: _ClassVar[OrderType]
    ORDER_TYPE_DRIVE_THRU: _ClassVar[OrderType]
ORDER_STATE_UNSPECIFIED: OrderState
ORDER_STATE_PAYMENT_PENDING: OrderState
ORDER_STATE_COMPLETE: OrderState
ORDER_STATE_CANCELED: OrderState
ORDER_STATE_PLACED: OrderState
PAYMENT_STATE_UNSPECIFIED: PaymentState
PAYMENT_STATE_COMPLETE: PaymentState
PAYMENT_STATE_FAILED: PaymentState
PAYMENT_STATE_PENDING: PaymentState
ORDER_TYPE_UNSPECIFIED: OrderType
ORDER_TYPE_DINE_IN: OrderType
ORDER_TYPE_TAKE_AWAY: OrderType
ORDER_TYPE_DRIVE_THRU: OrderType

class Order(_message.Message):
    __slots__ = ("OrderUuid", "StoreUuid", "UserPhoneNo", "OrderType", "TableNo", "VehicleNo", "VehicleDescription", "CouponName", "Items", "TotalAmount", "DiscountAmount", "FinalAmount", "PaymentState", "PaymentMethod", "SpecialInstruction", "OrderStatus", "CreatedAt", "UpdatedAt")
    ORDERUUID_FIELD_NUMBER: _ClassVar[int]
    STOREUUID_FIELD_NUMBER: _ClassVar[int]
    USERPHONENO_FIELD_NUMBER: _ClassVar[int]
    ORDERTYPE_FIELD_NUMBER: _ClassVar[int]
    TABLENO_FIELD_NUMBER: _ClassVar[int]
    VEHICLENO_FIELD_NUMBER: _ClassVar[int]
    VEHICLEDESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    COUPONNAME_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    TOTALAMOUNT_FIELD_NUMBER: _ClassVar[int]
    DISCOUNTAMOUNT_FIELD_NUMBER: _ClassVar[int]
    FINALAMOUNT_FIELD_NUMBER: _ClassVar[int]
    PAYMENTSTATE_FIELD_NUMBER: _ClassVar[int]
    PAYMENTMETHOD_FIELD_NUMBER: _ClassVar[int]
    SPECIALINSTRUCTION_FIELD_NUMBER: _ClassVar[int]
    ORDERSTATUS_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    UPDATEDAT_FIELD_NUMBER: _ClassVar[int]
    OrderUuid: str
    StoreUuid: str
    UserPhoneNo: str
    OrderType: OrderType
    TableNo: str
    VehicleNo: str
    VehicleDescription: str
    CouponName: str
    Items: _containers.RepeatedCompositeFieldContainer[OrderItem]
    TotalAmount: float
    DiscountAmount: float
    FinalAmount: float
    PaymentState: PaymentState
    PaymentMethod: str
    SpecialInstruction: str
    OrderStatus: OrderState
    CreatedAt: _timestamp_pb2.Timestamp
    UpdatedAt: _timestamp_pb2.Timestamp
    def __init__(self, OrderUuid: _Optional[str] = ..., StoreUuid: _Optional[str] = ..., UserPhoneNo: _Optional[str] = ..., OrderType: _Optional[_Union[OrderType, str]] = ..., TableNo: _Optional[str] = ..., VehicleNo: _Optional[str] = ..., VehicleDescription: _Optional[str] = ..., CouponName: _Optional[str] = ..., Items: _Optional[_Iterable[_Union[OrderItem, _Mapping]]] = ..., TotalAmount: _Optional[float] = ..., DiscountAmount: _Optional[float] = ..., FinalAmount: _Optional[float] = ..., PaymentState: _Optional[_Union[PaymentState, str]] = ..., PaymentMethod: _Optional[str] = ..., SpecialInstruction: _Optional[str] = ..., OrderStatus: _Optional[_Union[OrderState, str]] = ..., CreatedAt: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., UpdatedAt: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CreateOrderRequest(_message.Message):
    __slots__ = ("Order",)
    ORDER_FIELD_NUMBER: _ClassVar[int]
    Order: Order
    def __init__(self, Order: _Optional[_Union[Order, _Mapping]] = ...) -> None: ...

class OrderResponse(_message.Message):
    __slots__ = ("Success", "Order")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    Success: bool
    Order: Order
    def __init__(self, Success: bool = ..., Order: _Optional[_Union[Order, _Mapping]] = ...) -> None: ...

class GetOrderRequest(_message.Message):
    __slots__ = ("OrderUuid",)
    ORDERUUID_FIELD_NUMBER: _ClassVar[int]
    OrderUuid: str
    def __init__(self, OrderUuid: _Optional[str] = ...) -> None: ...

class UpdateOrderRequest(_message.Message):
    __slots__ = ("OrderUuid", "Order")
    ORDERUUID_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    OrderUuid: str
    Order: Order
    def __init__(self, OrderUuid: _Optional[str] = ..., Order: _Optional[_Union[Order, _Mapping]] = ...) -> None: ...

class DeleteOrderRequest(_message.Message):
    __slots__ = ("OrderUuid",)
    ORDERUUID_FIELD_NUMBER: _ClassVar[int]
    OrderUuid: str
    def __init__(self, OrderUuid: _Optional[str] = ...) -> None: ...

class ListOrderRequest(_message.Message):
    __slots__ = ("StoreUuid", "UserPhoneNo")
    STOREUUID_FIELD_NUMBER: _ClassVar[int]
    USERPHONENO_FIELD_NUMBER: _ClassVar[int]
    StoreUuid: str
    UserPhoneNo: str
    def __init__(self, StoreUuid: _Optional[str] = ..., UserPhoneNo: _Optional[str] = ...) -> None: ...

class ListOrderResponse(_message.Message):
    __slots__ = ("Orders",)
    ORDERS_FIELD_NUMBER: _ClassVar[int]
    Orders: _containers.RepeatedCompositeFieldContainer[Order]
    def __init__(self, Orders: _Optional[_Iterable[_Union[Order, _Mapping]]] = ...) -> None: ...

class OrderItem(_message.Message):
    __slots__ = ("ProductUuid", "Price", "Quantity", "Discount", "SubTotal", "TaxedAmount", "DiscountAmount")
    PRODUCTUUID_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    SUBTOTAL_FIELD_NUMBER: _ClassVar[int]
    TAXEDAMOUNT_FIELD_NUMBER: _ClassVar[int]
    DISCOUNTAMOUNT_FIELD_NUMBER: _ClassVar[int]
    ProductUuid: str
    Price: float
    Quantity: int
    Discount: float
    SubTotal: float
    TaxedAmount: float
    DiscountAmount: float
    def __init__(self, ProductUuid: _Optional[str] = ..., Price: _Optional[float] = ..., Quantity: _Optional[int] = ..., Discount: _Optional[float] = ..., SubTotal: _Optional[float] = ..., TaxedAmount: _Optional[float] = ..., DiscountAmount: _Optional[float] = ...) -> None: ...

class empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
