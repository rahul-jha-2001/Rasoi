import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(os.path.dirname(os.curdir))

from  datetime import datetime
import logging
from concurrent import futures
import grpc
import django,os
from django.core.exceptions import ValidationError
from django.db import transaction
import traceback
from decimal import Decimal as DecimalType
from dotenv import load_dotenv
from google.protobuf import empty_pb2
load_dotenv()



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Cart.settings')
django.setup()

logger = logging.getLogger(__name__)
from api.models import Cart,CartItem,Coupon
from proto import Cart_pb2,Cart_pb2_grpc

    
class CartService(Cart_pb2_grpc.CartServiceServicer):


    def _CartItem_to_response(self,item:CartItem) -> CartItem:
            response  = Cart_pb2.CartItem(
                ProductUuid = str(item.ProductUuid),
                Price= float(item.Price),
                Quantity= item.Quantity,
                Discount= float(item.Discount),
                SubTotal= float(item.subtotal)
            )
            return response
        
    def _Cart_to_response(self,cart:Cart) -> Cart_pb2.CartResponse:
    
        response = Cart_pb2.CartResponse(
            StoreUuid = str(cart.StoreUuid),
            UserPhoneNo = str(cart.UserPhoneNo),
            OrderType= str(cart.OrderType),
            TableNo= str(cart.TableNo),
            VehicleNo= str(cart.VehicleNo),
            VehicleDescription=str(cart.VehicleDescription),
            CouponName= str(cart.CouponName),
            Items =[self._CartItem_to_response(x) 
                    for x in cart.Items.all()],
            TotalAmount= float(cart.TotalAmounts)
        )
        return response  
    def _ValidCartResponse(self,coupon:Coupon,cart:Cart):

        response = Cart_pb2.ValidCouponResponse(
            Cart=self._Cart_to_response(cart),
            valid = coupon.is_Vaild(cart)[0],
            ValidationMessage= coupon.is_Vaild(cart)[1]
        )
        return response
    @transaction.atomic
    def CreateCart(self, request, context):
        try:
            if Cart.objects.get(StoreUuid = request.Cart.StoreUuid,UserPhoneNo = request.Cart.UserPhoneNo):
                cart = Cart.objects.get(StoreUuid = request.Cart.StoreUuid,UserPhoneNo = request.Cart.UserPhoneNo)
                cart.OrderType = request.OrderType
                cart.TableNo = request.TableNo
                cart.VehicleNo = request.VehicleNo
                cart.VehicleDescription = request.VehicleDescription
                cart.CouponName = request.CouponName
                cart.full_clean()
                cart.save()
                return self._Cart_to_response(cart)
        except ValidationError as e:
            logger.error(f"Validation Error : {str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT,str(e)) 
        except Cart.DoesNotExist:
            pass    
        try:
            cart = Cart.objects.create(
                StoreUuid = request.Cart.StoreUuid,
                UserPhoneNo = request.Cart.UserPhoneNo,
                OrderType = request.OrderType,
                TableNo = request.TableNo or None,
                VehicleNo = request.VehicleNo or None,
                VehicleDescription = request.VehicleDescription or None,
                CouponName = request.CouponName or None
            )
            logger.info(f"Cart Created for {cart.UserPhoneNo} at  {cart.StoreUuid}")
            return self._Cart_to_response(cart)
        except ValidationError as e:
            logger.error(f"Validation Error : {str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT,str(e))
        except Exception as e:
            logger.error(f"Error Creating cart:{str(e)} {str(traceback.format_exc())},{str(traceback.format_exc())}")
            context.abort(grpc.StatusCode.INTERNAL,"Internal Server Error")
    def GetCart(self, request, context):
        try:
            cart = Cart.objects.get(StoreUuid = request.Cart.StoreUuid,UserPhoneNo = request.Cart.UserPhoneNo)
            return self._Cart_to_response(cart)
        except Cart.DoesNotExist:
            logger.error(f"Cart Does Not Exist For {request.Cart.StoreUuid} and {request.Cart.UserPhoneNo}")
            context.abort(grpc.StatusCode.NOT_FOUND,f"Cart Does Not Exist For {request.Cart.StoreUuid} and {request.Cart.UserPhoneNo}")
        except Exception as e :
            logger.error(f"Error getting Cart:{str(e)} {str(traceback.format_exc())} {str(traceback.format_exc())}")
            context.abort(grpc.StatusCode.INTERNAL,f"Internal Server Error")
    @transaction.atomic
    def UpdateCart(self, request, context):
        try:
            cart = Cart.objects.get(StoreUuid = request.Cart.StoreUuid,UserPhoneNo = request.Cart.UserPhoneNo)
        except Cart.DoesNotExist:
            logger.error(f"Cart Does Not Exist For {request.Cart.StoreUuid} and {request.Cart.UserPhoneNo}")
            context.abort(grpc.StatusCode.NOT_FOUND,f"Cart Does Not Exist For {request.Cart.StoreUuid} and {request.Cart.UserPhoneNo}")
        logger.info(request)
        try:
            if request.HasField("OrderType"):
                 cart.OrderType = request.OrderType
            if request.HasField('TableNo'):
                cart.TableNo = request.TableNo
            if request.HasField('VehicleNo'):
                cart.VehicleNo = request.VehicleNo    
            if request.HasField('VehicleDescription'):
                cart.VehicleDescription = request.VehicleDescription
            if request.HasField('CouponName'):
                cart.CouponName = request.CouponName
            cart.full_clean()
            cart.save() 
            logger.info(f"Cart Updated for {cart.StoreUuid} and {cart.UserPhoneNo}")
            return self._Cart_to_response(cart)
        except ValidationError as  e:
            logger.error(f"Validation error {str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT,str(e))
        except Exception as e:
            logger.error(f"Error Updating Cart :{str(e)} {str(traceback.format_exc())} {str(traceback.format_exc())}")
            context.abort(grpc.StatusCode.INTERNAL,f"Internal Server error {str(e)} ")
    @transaction.atomic
    def DeleteCart(self, request, context):
        try:
            cart = Cart.objects.get(StoreUuid = request.Cart.StoreUuid,UserPhoneNo = request.Cart.UserPhoneNo)
        except Cart.DoesNotExist:
            logger.error(f"Cart does not exist for store {request.Cart.StoreUuid} and UserPhoneNo {request.Cart.UserPhoneNo}")    
            context.abort(grpc.StatusCode.NOT_FOUND,f"Cart does not exist for store {request.Cart.StoreUuid} and UserPhoneNo {request.Cart.UserPhoneNo}")
        temp = cart.delete()
        logger.info(f"Following Entites deleted {str(temp)} ") 
        return Cart_pb2.Empty()
    @transaction.atomic
    def AddCartItem(self, request, context):
        try:
            cart = Cart.objects.get(StoreUuid = request.Cart.StoreUuid,UserPhoneNo = request.Cart.UserPhoneNo)
        except Cart.DoesNotExist:
            logger.error(f"Cart does not exist for store {request.Cart.StoreUuid} and UserPhoneNo {request.Cart.UserPhoneNo}")    
            context.abort(grpc.StatusCode.NOT_FOUND,f"Cart does not exist for store {request.Cart.StoreUuid} and UserPhoneNo {request.Cart.UserPhoneNo}")
        try:    
            cartitem = CartItem.objects.create(CartId = cart,
                                               ProductUuid = request.item.ProductUuid,
                                               Price = request.item.Price,
                                               Quantity = request.item.Quantity,
                                               Discount = request.item.Discount
                                               )
            logger.info(f"{cartitem.ProductUuid} Item created for {cart.StoreUuid} and phone {cart.UserPhoneNo}")
            return self._Cart_to_response(cart)
        except Exception as e:
            logger.error(f"Error Adding Item to  Cart :{str(e)} {str(traceback.format_exc())}")
            context.abort(grpc.StatusCode.INTERNAL,f"Internal Server error {str(e)}")  
    @transaction.atomic
    def RemoveCartItem(self, request, context):
        try:
            cart = Cart.objects.get(StoreUuid = request.Cart.StoreUuid,UserPhoneNo = request.Cart.UserPhoneNo)
        except Cart.DoesNotExist:
            logger.error(f"Cart does not exist for store {request.Cart.StoreUuid} and UserPhoneNo {request.Cart.UserPhoneNo}")    
            context.abort(grpc.StatusCode.NOT_FOUND,f"Cart does not exist for store {request.Cart.StoreUuid} and UserPhoneNo {request.Cart.UserPhoneNo}")
        try:
            item = cart.Items.filter(ProductUuid = request.ProductUuid)
            tmp = item.delete()
            logger.info(f"Entites removed {tmp}")
            return self._Cart_to_response(cart)
        except Exception as e:
            logger.error(f"Error Updating CartItem :{str(e)} {str(traceback.format_exc())}")
            context.abort(grpc.StatusCode.INTERNAL,f"Internal Server error {str(e)}")
    @transaction.atomic
    def AddQuantity(self, request, context):
        try:
            cart = Cart.objects.get(StoreUuid = request.Cart.StoreUuid,UserPhoneNo = request.Cart.UserPhoneNo)
        except Cart.DoesNotExist:
            logger.error(f"Cart does not exist for store {request.Cart.StoreUuid} and UserPhoneNo {request.Cart.UserPhoneNo}")    
            context.abort(grpc.StatusCode.NOT_FOUND,f"Cart does not exist for store {request.Cart.StoreUuid} and UserPhoneNo {request.Cart.UserPhoneNo}")
        try:
            item = cart.Items.all().get(ProductUuid = request.ProductUuid)
            item.add_quantity(request.Quantity)
            return(self._Cart_to_response(cart))
        except CartItem.DoesNotExist:
            logger.error(f"Item for productUuid {request.ProductUuid} dose not exist in cart with SToreUuid{request.Cart.StoreUuid} UserPhoneNo {request.Cart.UserPhoneNo}")    
            context.abort(grpc.StatusCode.NOT_FOUND,f"Item for productUuid {request.ProductUuid} dose not exist in cart with SToreUuid{request.Cart.StoreUuid} UserPhoneNo {request.Cart.UserPhoneNo}")
    @transaction.atomic
    def RemoveQuantity(self, request, context):
        try:
            cart = Cart.objects.get(StoreUuid = request.Cart.StoreUuid,UserPhoneNo = request.Cart.UserPhoneNo)
        except Cart.DoesNotExist:
            logger.error(f"Cart does not exist for store {request.Cart.StoreUuid} and UserPhoneNo {request.Cart.UserPhoneNo}")    
            context.abort(grpc.StatusCode.NOT_FOUND,f"Cart does not exist for store {request.Cart.StoreUuid} and UserPhoneNo {request.Cart.UserPhoneNo}")
        try:
            item = cart.Items.all().get(ProductUuid = request.ProductUuid)
            item.remove_quantity(request.Quantity)
            logger.info(f"remove Quantity {request.Quantity} for ProductUuid {request.ProductUuid}")
            return(self._Cart_to_response(cart))
        except CartItem.DoesNotExist:
            logger.error(f"Item for productUuid {request.ProductUuid} dose not exist in cart with SToreUuid{request.Cart.StoreUuid} UserPhoneNo {request.Cart.UserPhoneNo}")    
            context.abort(grpc.StatusCode.NOT_FOUND,f"Item for productUuid {request.ProductUuid} dose not exist in cart with SToreUuid{request.Cart.StoreUuid} UserPhoneNo {request.Cart.UserPhoneNo}")
    def ValidateCoupon(self, request, context):
        try:
            cart = Cart.objects.get(StoreUuid = request.Cart.StoreUuid,UserPhoneNo = request.Cart.UserPhoneNo)
            coup =  Coupon.objects.get(StoreUuid = request.StoreUuid,CouponCode = request.CouponCode)
        except Cart.DoesNotExist:
            logger.error(f"Cart Does Not Exist For {request.Cart.StoreUuid} and {request.Cart.UserPhoneNo}")
            context.abort(grpc.StatusCode.NOT_FOUND,f"Cart Does Not Exist For {request.Cart.StoreUuid} and {request.Cart.UserPhoneNo}")
        except Coupon.DoesNotExist:

            logger.error(f"Coupon Does Not Exist For {request.StoreUuid} and  couponcode {request.CouponCode}")
            return Cart_pb2.ValidCouponResponse(Cart= self._Cart_to_response(cart),
                                                valid=False,
                                                ValidationMessage="The coupon is Not Valid")
        except Exception as e :
            logger.error(f"Error getting Cart or coupon :{str(e)} {str(traceback.format_exc())} {str(traceback.format_exc())}")
            context.abort(grpc.StatusCode.INTERNAL,f"Internal Server Error")
        if not coup.is_Vaild(cart)[0]:
            return self._ValidCartResponse(coup,cart)
        cart.ApplyDiscount(coup.Discount)
        cart.CouponName = coup.CouponCode
        cart.save()
        logger.info(f"Cooupon Is Vaild and Applied to the CartItem")
        return self._ValidCartResponse(coup,cart)

class CouponService(Cart_pb2_grpc.CouponServiceServicer):
    
    def _Coupon_to_response(self,coupon:Coupon):

        response = Cart_pb2.CouponResponse(
            Coupon = Cart_pb2.Coupon(
                StoreUuid = str(coupon.StoreUuid),
                CouponCode= str(coupon.CouponCode),
                VaildFrom= datetime(coupon.VaildFrom.year,coupon.VaildFrom.month,coupon.VaildFrom.day),
                VaildTo= datetime(coupon.VaildTo.year,coupon.VaildTo.month,coupon.VaildTo.day),
                Discount= float(coupon.Discount),
                MinSpend= float(coupon.MinSpend)
            )
        )
        return response
    @transaction.atomic
    def CreateCoupon(self,request,context):
        logger.debug(str(datetime.fromtimestamp(request.Coupon.VaildFrom.seconds).date()))
        try:
            coup = Coupon.objects.create(
                StoreUuid = request.Coupon.StoreUuid,
                CouponCode = request.Coupon.CouponCode,
                VaildFrom = datetime.fromtimestamp(request.Coupon.VaildFrom.seconds).date(),
                VaildTo = datetime.fromtimestamp(request.Coupon.VaildTo.seconds).date(),
                Discount = request.Coupon.Discount,
                MinSpend = request.Coupon.MinSpend
            )
            logger.info(f"{coup.CouponCode} Created for {coup.StoreUuid}")
            return self._Coupon_to_response(coup)
        except ValidationError as e:
            logger.error(f"Validation Error : {str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT,str(e))
        except Exception as e:
            logger.error(f"Error Creating CartItem :{str(e)} {str(traceback.format_exc())}")
            context.abort(grpc.StatusCode.INTERNAL,f"Internal Server error {str(e)}")        
    def GetCoupon(self,request,context):
        try:
            coup = Coupon.objects.get(StoreUuid = request.StoreUuid,CouponCode = request.CouponCode)
            return self._Coupon_to_response(coup)
        except Coupon.DoesNotExist:
            logger.error(f"Coupon Does Not Exist For {request.StoreUuid} and {request.CouponCode}")
            context.abort(grpc.StatusCode.NOT_FOUND,f"Coupon Does Not Exist For {request.StoreUuid} and {request.CouponCode}")
        except Exception as e :
            logger.error(f"Error getting Coupon:{str(e)} {str(traceback.format_exc())} {str(traceback.format_exc())}")
            context.abort(grpc.StatusCode.INTERNAL,f"Internal Server Error")
    @transaction.atomic
    def UpdateCoupon(self,request,context):
        try:
            coup = Coupon.objects.get(StoreUuid = request.StoreUuid,CouponCode = request.CouponCode)
        except Coupon.DoesNotExist:
            logger.error(f"Coupon Does Not Exist For {request.Coupon.StoreUuid} and {request.Coupon.CouponCode}")
            context.abort(grpc.StatusCode.NOT_FOUND,f"Coupon Does Not Exist For {request.Coupon.StoreUuid} and {request.Coupon.CouponCode}")
        except Exception as e :
            logger.error(f"Error getting Coupon:{str(e)} {str(traceback.format_exc())} {str(traceback.format_exc())}")
            context.abort(grpc.StatusCode.INTERNAL,f"Internal Server Error")

        try:    
            if request.Coupon.HasField("VaildFrom"):
                 coup.VaildFrom = datetime.fromtimestamp(request.Coupon.VaildFrom.seconds).date()
            if request.Coupon.HasField("VaildTo"):
                 coup.VaildTo = datetime.fromtimestamp(request.Coupon.VaildTo.seconds).date()
            if request.Coupon.HasField("Discount"):
                 coup.Discount = request.Coupon.Discount
            if request.Coupon.HasField("MinSpend"):
                 coup.MinSpend = request.Coupon.MinSpend
            coup.CouponCode = request.Coupon.CouponCode     
            coup.full_clean()
            coup.save()
            logger.info(f"Successfully Updated coupon {request.Coupon.CouponCode} for StoreId {request.Coupon.StoreUuid}")     
            return self._Coupon_to_response(coupon=coup)
        except ValidationError as  e:
            logger.error(f"Validation error {str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT,str(e))
        except Exception as e:
            logger.error(f"Error Updating coupon :{str(e)} {str(traceback.format_exc())} {str(traceback.format_exc())}")
            context.abort(grpc.StatusCode.INTERNAL,f"Internal Server error {str(e)} ")
    @transaction.atomic
    def DeleteCoupon(self,request,context):
        try:
            coup = Coupon.objects.get(StoreUuid = request.StoreUuid,CouponCode = request.CouponCode)
        except Cart.DoesNotExist:
            return 
            logger.error(f"Coupon does not exist for store {request.StoreUuid} and UserPhoneNo {request.CouponCode}")    
            context.abort(grpc.StatusCode.NOT_FOUND,f"Coupon does not exist for store {request.StoreUuid} and CouponCode {request.CouponCode}")
        temp = coup.delete()
        logger.info(f"Following Entites deleted {str(temp)} ") 
        return Cart_pb2.Empty()
            





def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    Cart_pb2_grpc.add_CartServiceServicer_to_server(CartService(),server)
    Cart_pb2_grpc.add_CouponServiceServicer_to_server(CouponService(),server)

    grpc_port = os.getenv('GRPC_SERVER_PORT', '50051')

    server.add_insecure_port(f"[::]:{grpc_port}")
    server.start()
    logger.info(f"Server Stated at {grpc_port}")
    server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig(level= logging.INFO)
    serve()
