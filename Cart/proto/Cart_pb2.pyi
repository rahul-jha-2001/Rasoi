from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OrderType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Unspecified: _ClassVar[OrderType]
    DineIn: _ClassVar[OrderType]
    TakeAway: _ClassVar[OrderType]
    DriveThru: _ClassVar[OrderType]
Unspecified: OrderType
DineIn: OrderType
TakeAway: OrderType
DriveThru: OrderType

class Coupon(_message.Message):
    __slots__ = ("StoreUuid", "CouponCode", "VaildFrom", "VaildTo", "Discount", "MinSpend")
    STOREUUID_FIELD_NUMBER: _ClassVar[int]
    COUPONCODE_FIELD_NUMBER: _ClassVar[int]
    VAILDFROM_FIELD_NUMBER: _ClassVar[int]
    VAILDTO_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    MINSPEND_FIELD_NUMBER: _ClassVar[int]
    StoreUuid: str
    CouponCode: str
    VaildFrom: _timestamp_pb2.Timestamp
    VaildTo: _timestamp_pb2.Timestamp
    Discount: float
    MinSpend: float
    def __init__(self, StoreUuid: _Optional[str] = ..., CouponCode: _Optional[str] = ..., VaildFrom: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., VaildTo: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., Discount: _Optional[float] = ..., MinSpend: _Optional[float] = ...) -> None: ...

class ValidCartResquest(_message.Message):
    __slots__ = ("Cart", "StoreUuid", "CouponCode")
    CART_FIELD_NUMBER: _ClassVar[int]
    STOREUUID_FIELD_NUMBER: _ClassVar[int]
    COUPONCODE_FIELD_NUMBER: _ClassVar[int]
    Cart: CartIdentifier
    StoreUuid: str
    CouponCode: str
    def __init__(self, Cart: _Optional[_Union[CartIdentifier, _Mapping]] = ..., StoreUuid: _Optional[str] = ..., CouponCode: _Optional[str] = ...) -> None: ...

class CreateCouponRequest(_message.Message):
    __slots__ = ("Coupon",)
    COUPON_FIELD_NUMBER: _ClassVar[int]
    Coupon: Coupon
    def __init__(self, Coupon: _Optional[_Union[Coupon, _Mapping]] = ...) -> None: ...

class GetCouponRequest(_message.Message):
    __slots__ = ("StoreUuid", "CouponCode")
    STOREUUID_FIELD_NUMBER: _ClassVar[int]
    COUPONCODE_FIELD_NUMBER: _ClassVar[int]
    StoreUuid: str
    CouponCode: str
    def __init__(self, StoreUuid: _Optional[str] = ..., CouponCode: _Optional[str] = ...) -> None: ...

class UpdateCouponRequest(_message.Message):
    __slots__ = ("StoreUuid", "CouponCode", "Coupon")
    STOREUUID_FIELD_NUMBER: _ClassVar[int]
    COUPONCODE_FIELD_NUMBER: _ClassVar[int]
    COUPON_FIELD_NUMBER: _ClassVar[int]
    StoreUuid: str
    CouponCode: str
    Coupon: Coupon
    def __init__(self, StoreUuid: _Optional[str] = ..., CouponCode: _Optional[str] = ..., Coupon: _Optional[_Union[Coupon, _Mapping]] = ...) -> None: ...

class DeleteCouponRequest(_message.Message):
    __slots__ = ("StoreUuid", "CouponCode")
    STOREUUID_FIELD_NUMBER: _ClassVar[int]
    COUPONCODE_FIELD_NUMBER: _ClassVar[int]
    StoreUuid: str
    CouponCode: str
    def __init__(self, StoreUuid: _Optional[str] = ..., CouponCode: _Optional[str] = ...) -> None: ...

class CouponResponse(_message.Message):
    __slots__ = ("Coupon",)
    COUPON_FIELD_NUMBER: _ClassVar[int]
    Coupon: Coupon
    def __init__(self, Coupon: _Optional[_Union[Coupon, _Mapping]] = ...) -> None: ...

class ValidCouponResponse(_message.Message):
    __slots__ = ("Cart", "valid", "ValidationMessage")
    CART_FIELD_NUMBER: _ClassVar[int]
    VALID_FIELD_NUMBER: _ClassVar[int]
    VALIDATIONMESSAGE_FIELD_NUMBER: _ClassVar[int]
    Cart: CartResponse
    valid: bool
    ValidationMessage: str
    def __init__(self, Cart: _Optional[_Union[CartResponse, _Mapping]] = ..., valid: bool = ..., ValidationMessage: _Optional[str] = ...) -> None: ...

class CartItem(_message.Message):
    __slots__ = ("ProductUuid", "Price", "Quantity", "Discount", "SubTotal")
    PRODUCTUUID_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    SUBTOTAL_FIELD_NUMBER: _ClassVar[int]
    ProductUuid: str
    Price: float
    Quantity: int
    Discount: float
    SubTotal: float
    def __init__(self, ProductUuid: _Optional[str] = ..., Price: _Optional[float] = ..., Quantity: _Optional[int] = ..., Discount: _Optional[float] = ..., SubTotal: _Optional[float] = ...) -> None: ...

class CreateCartRequest(_message.Message):
    __slots__ = ("Cart", "OrderType", "TableNo", "VehicleNo", "VehicleDescription", "CouponName")
    CART_FIELD_NUMBER: _ClassVar[int]
    ORDERTYPE_FIELD_NUMBER: _ClassVar[int]
    TABLENO_FIELD_NUMBER: _ClassVar[int]
    VEHICLENO_FIELD_NUMBER: _ClassVar[int]
    VEHICLEDESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    COUPONNAME_FIELD_NUMBER: _ClassVar[int]
    Cart: CartIdentifier
    OrderType: OrderType
    TableNo: str
    VehicleNo: str
    VehicleDescription: str
    CouponName: str
    def __init__(self, Cart: _Optional[_Union[CartIdentifier, _Mapping]] = ..., OrderType: _Optional[_Union[OrderType, str]] = ..., TableNo: _Optional[str] = ..., VehicleNo: _Optional[str] = ..., VehicleDescription: _Optional[str] = ..., CouponName: _Optional[str] = ...) -> None: ...

class CartResponse(_message.Message):
    __slots__ = ("StoreUuid", "UserPhoneNo", "OrderType", "TableNo", "VehicleNo", "VehicleDescription", "CouponName", "Items", "TotalAmount")
    STOREUUID_FIELD_NUMBER: _ClassVar[int]
    USERPHONENO_FIELD_NUMBER: _ClassVar[int]
    ORDERTYPE_FIELD_NUMBER: _ClassVar[int]
    TABLENO_FIELD_NUMBER: _ClassVar[int]
    VEHICLENO_FIELD_NUMBER: _ClassVar[int]
    VEHICLEDESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    COUPONNAME_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    TOTALAMOUNT_FIELD_NUMBER: _ClassVar[int]
    StoreUuid: str
    UserPhoneNo: str
    OrderType: str
    TableNo: str
    VehicleNo: str
    VehicleDescription: str
    CouponName: str
    Items: _containers.RepeatedCompositeFieldContainer[CartItem]
    TotalAmount: float
    def __init__(self, StoreUuid: _Optional[str] = ..., UserPhoneNo: _Optional[str] = ..., OrderType: _Optional[str] = ..., TableNo: _Optional[str] = ..., VehicleNo: _Optional[str] = ..., VehicleDescription: _Optional[str] = ..., CouponName: _Optional[str] = ..., Items: _Optional[_Iterable[_Union[CartItem, _Mapping]]] = ..., TotalAmount: _Optional[float] = ...) -> None: ...

class CartIdentifier(_message.Message):
    __slots__ = ("StoreUuid", "UserPhoneNo")
    STOREUUID_FIELD_NUMBER: _ClassVar[int]
    USERPHONENO_FIELD_NUMBER: _ClassVar[int]
    StoreUuid: str
    UserPhoneNo: str
    def __init__(self, StoreUuid: _Optional[str] = ..., UserPhoneNo: _Optional[str] = ...) -> None: ...

class GetCartRequest(_message.Message):
    __slots__ = ("Cart",)
    CART_FIELD_NUMBER: _ClassVar[int]
    Cart: CartIdentifier
    def __init__(self, Cart: _Optional[_Union[CartIdentifier, _Mapping]] = ...) -> None: ...

class UpdateCartRequest(_message.Message):
    __slots__ = ("Cart", "OrderType", "TableNo", "VehicleNo", "VehicleDescription", "CouponName")
    CART_FIELD_NUMBER: _ClassVar[int]
    ORDERTYPE_FIELD_NUMBER: _ClassVar[int]
    TABLENO_FIELD_NUMBER: _ClassVar[int]
    VEHICLENO_FIELD_NUMBER: _ClassVar[int]
    VEHICLEDESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    COUPONNAME_FIELD_NUMBER: _ClassVar[int]
    Cart: CartIdentifier
    OrderType: OrderType
    TableNo: str
    VehicleNo: str
    VehicleDescription: str
    CouponName: str
    def __init__(self, Cart: _Optional[_Union[CartIdentifier, _Mapping]] = ..., OrderType: _Optional[_Union[OrderType, str]] = ..., TableNo: _Optional[str] = ..., VehicleNo: _Optional[str] = ..., VehicleDescription: _Optional[str] = ..., CouponName: _Optional[str] = ...) -> None: ...

class AddItemRequest(_message.Message):
    __slots__ = ("Cart", "item")
    CART_FIELD_NUMBER: _ClassVar[int]
    ITEM_FIELD_NUMBER: _ClassVar[int]
    Cart: CartIdentifier
    item: CartItem
    def __init__(self, Cart: _Optional[_Union[CartIdentifier, _Mapping]] = ..., item: _Optional[_Union[CartItem, _Mapping]] = ...) -> None: ...

class RemoveItemRequest(_message.Message):
    __slots__ = ("Cart", "ProductUuid")
    CART_FIELD_NUMBER: _ClassVar[int]
    PRODUCTUUID_FIELD_NUMBER: _ClassVar[int]
    Cart: CartIdentifier
    ProductUuid: str
    def __init__(self, Cart: _Optional[_Union[CartIdentifier, _Mapping]] = ..., ProductUuid: _Optional[str] = ...) -> None: ...

class DeleteCartItemRequest(_message.Message):
    __slots__ = ("Cart", "ProductUuid")
    CART_FIELD_NUMBER: _ClassVar[int]
    PRODUCTUUID_FIELD_NUMBER: _ClassVar[int]
    Cart: CartIdentifier
    ProductUuid: str
    def __init__(self, Cart: _Optional[_Union[CartIdentifier, _Mapping]] = ..., ProductUuid: _Optional[str] = ...) -> None: ...

class QuantityRequest(_message.Message):
    __slots__ = ("Cart", "ProductUuid", "Quantity")
    CART_FIELD_NUMBER: _ClassVar[int]
    PRODUCTUUID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    Cart: CartIdentifier
    ProductUuid: str
    Quantity: int
    def __init__(self, Cart: _Optional[_Union[CartIdentifier, _Mapping]] = ..., ProductUuid: _Optional[str] = ..., Quantity: _Optional[int] = ...) -> None: ...

class DeleteCartRequest(_message.Message):
    __slots__ = ("Cart",)
    CART_FIELD_NUMBER: _ClassVar[int]
    Cart: CartIdentifier
    def __init__(self, Cart: _Optional[_Union[CartIdentifier, _Mapping]] = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
