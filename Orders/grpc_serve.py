import sys
import os
from  datetime import datetime
import logging
from concurrent import futures
import grpc
import django,os
from django.core.exceptions import ValidationError
from django.db import transaction
import traceback
from decimal import Decimal as DecimalType
from google.protobuf.timestamp_pb2 import Timestamp

from dotenv import load_dotenv


sys.path.append(os.getcwd()+r"\Orders\proto")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Orders.settings')
django.setup()


from Order.models import Order,OrderItem
from proto import Order_pb2,Order_pb2_grpc


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG for most detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Output to console
        logging.FileHandler('order_grpc_service.log')  # Optional: log to file
    ]
)

flag = load_dotenv()
logger.info(f"Varibles loaded in GRPC server {flag}")

class OrderService(Order_pb2_grpc.OrderServiceServicer):
    
    def _OrderItem_to_response(self,item:OrderItem) -> OrderItem:
        response  = Order_pb2.OrderItem(
            ProductUuid = str(item.ProductUuid),
            Price= float(item.Price),
            Quantity= item.Quantity,
            Discount= float(item.Discount),
            SubTotal= float(item.Subtotal),
            TaxedAmount = float(item.TaxedAmount),
            DiscountAmount = float(item.DiscountAmount)
        )
        return response
        
    def _Order_to_response(self,Order:Order)-> Order_pb2.Order:
        
        def datetime_to_timestamp(dt):
            if dt:
                timestamp = Timestamp()
                timestamp.FromDatetime(dt)
                return timestamp
            return None
        # Insert where you want to pause


        response = Order_pb2.Order(

            OrderUuid= str(Order.OrderUuid),
            StoreUuid= str(Order.StoreUuid),
            UserPhoneNo= str(Order.UserPhoneNo),
            OrderType= int(Order.OrderType),
            TableNo= str(Order.TableNo),
            VehicleNo= str(Order.VehicleNo),
            VehicleDescription= str(Order.VehicleDescription),
            CouponName= str(Order.CouponName),
            Items= [self._OrderItem_to_response(x) for x in Order.Items.all()],

            TotalAmount= float(Order.TotalAmount),
            DiscountAmount = float(Order.DiscountAmount),
            FinalAmount =  float(Order.FinalAmount),

            PaymentState= int(Order.PaymentStatus),
            PaymentMethod= str(Order.PaymentMethod),

            SpecialInstruction= str(Order.SpecialInstruction),

            OrderStatus = int(Order.OrderStatus),
            
            
            CreatedAt=datetime_to_timestamp(Order.created_at),
            UpdatedAt=datetime_to_timestamp(Order.updated_at),
        ) 
        return response
    
    def _Order_to_OrderResponses(self,order:Order = None,Success:bool = True ) -> Order_pb2.OrderResponse:
            response = Order_pb2.OrderResponse(
                Success= Success,
                Order=self._Order_to_response(order)
            )
            return response
    
    def GetOrder(self, request, context):
        try:
            order = Order.objects.get(OrderUuid = request.OrderUuid)
            return self._Order_to_OrderResponses(order)
        except Order.DoesNotExist:
            logger.error(f"Order does not exist for OrderUuid {request.OrderUuid}")
            context.abort(grpc.StatusCode.NOT_FOUND,f"Order does not exist for OrderUuid {request.OrderUuid}")
            
        except ValidationError as e:
            logger.error(f"Validation Error :{str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT,str(e))

        except Exception as e:
            print(str(e), str(traceback.format_exc()))
            logger.error(f"Error Geting order:{str(e)} {str(traceback.format_exc())},{str(traceback.format_exc())}")
            context.abort(grpc.StatusCode.INTERNAL,"Internal Server Error")

    

    @transaction.atomic
    def CreateOrder(self, request, context):
        try:
            # First, check if an order with the same store and phone number already exists
            existing_order = Order.objects.filter(
                StoreUuid=request.Order.StoreUuid, 
                UserPhoneNo=request.Order.UserPhoneNo
            ).first()

            if existing_order:
                # If order exists, return the existing order
                return self._Order_to_OrderResponses(existing_order)

            # If no existing order, create a new one
            order = Order.objects.create(
                StoreUuid=request.Order.StoreUuid,
                UserPhoneNo=request.Order.UserPhoneNo,
                OrderType=request.Order.OrderType,
                TableNo=request.Order.TableNo,
                VehicleNo=request.Order.VehicleNo,
                VehicleDescription=request.Order.VehicleDescription,
                CouponName=request.Order.CouponName,
                TotalAmount=request.Order.TotalAmount,
                DiscountAmount=request.Order.DiscountAmount,
                FinalAmount=request.Order.FinalAmount,
                PaymentStatus=request.Order.PaymentState,
                PaymentMethod=request.Order.PaymentMethod,
                SpecialInstruction=request.Order.SpecialInstruction,
                OrderStatus=request.Order.OrderStatus
            )

            # Create OrderItems
            for item_request in request.Order.Items:
                OrderItem.objects.create(
                    Order=order,
                    ProductUuid=item_request.ProductUuid,
                    Price=item_request.Price,
                    Quantity=item_request.Quantity,
                    Discount=item_request.Discount,
                    Subtotal=item_request.SubTotal,
                    TaxedAmount=item_request.TaxedAmount,
                    DiscountAmount=item_request.DiscountAmount
                )
            logger.info(f"Order created for {order.__str__()} with OrderId {order.OrderUuid}")
            return self._Order_to_OrderResponses(order)

        except ValidationError as e:
            logger.error(f"Validation Error: {str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
            return self._Order_to_OrderResponses(None)
        except Exception as e:
            logger.error(f"Error creating order: {str(e)} {str(traceback.format_exc())}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal Server Error")
    @transaction.atomic
    def UpdateOrder(self, request, context):
        try:
            # Find the existing order by OrderUuid
            existing_order = Order.objects.filter(OrderUuid=request.OrderUuid).first()

            if not existing_order:
                logger.error(f"Order does not exist for OrderUuid {request.OrderUuid}")
                context.abort(grpc.StatusCode.NOT_FOUND, f"Order does not exist for OrderUuid {request.OrderUuid}")

            # Update order fields
            existing_order.StoreUuid = request.Order.StoreUuid
            existing_order.UserPhoneNo = request.Order.UserPhoneNo
            existing_order.OrderType = request.Order.OrderType
            existing_order.TableNo = request.Order.TableNo
            existing_order.VehicleNo = request.Order.VehicleNo
            existing_order.VehicleDescription = request.Order.VehicleDescription
            existing_order.CouponName = request.Order.CouponName
            existing_order.TotalAmount = request.Order.TotalAmount
            existing_order.DiscountAmount = request.Order.DiscountAmount
            existing_order.FinalAmount = request.Order.FinalAmount
            existing_order.PaymentStatus = request.Order.PaymentState
            existing_order.PaymentMethod = request.Order.PaymentMethod
            existing_order.SpecialInstruction = request.Order.SpecialInstruction
            existing_order.OrderStatus = request.Order.OrderStatus

            # Save the updated order
            existing_order.save()

            # Delete existing order items and recreate
            existing_order.Items.all().delete()
            for item_request in request.Order.Items:
                OrderItem.objects.create(
                    Order=existing_order,
                    ProductUuid=item_request.ProductUuid,
                    Price=item_request.Price,
                    Quantity=item_request.Quantity,
                    Discount=item_request.Discount,
                    Subtotal=item_request.SubTotal,
                    TaxedAmount=item_request.TaxedAmount,
                    DiscountAmount=item_request.DiscountAmount
                )

            logger.info(f"Order updated for {existing_order.__str__()} with OrderId {existing_order.OrderUuid}")
            return self._Order_to_OrderResponses(existing_order)

        except ValidationError as e:
            logger.error(f"Validation Error: {str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
            return self._Order_to_OrderResponses(None)
        except Exception as e:
            logger.error(f"Error updating order: {str(e)} {str(traceback.format_exc())}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal Server Error")


    def DeleteOrder(self, request, context):
        try:
            order = Order.objects.filter(OrderUuid=request.OrderUuid).first()
            
            if not order:
                logger.error(f"Order not found: {request.OrderUuid}")
                context.abort(grpc.StatusCode.NOT_FOUND, f"Order not found: {request.OrderUuid}")
            
            order.delete()
            logger.info(f"Order deleted: {request.OrderUuid}")
            
            return Order_pb2.empty()

        except ValidationError as e:
            logger.error(f"Validation Error: {str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except Exception as e:
            logger.error(f"Error deleting order: {str(e)} {str(traceback.format_exc())}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal Server Error")

    def ListOrder(self, request, context):
        try:
            # Filter orders by StoreUuid and UserPhoneNo if provided
            filters = {}
            if request.StoreUuid:
                filters['StoreUuid'] = request.StoreUuid
            if request.UserPhoneNo:
                filters['UserPhoneNo'] = request.UserPhoneNo
            
            orders = Order.objects.filter(**filters)
            
            if not orders:
                logger.warning(f"No orders found for filters: {filters}")
            
            # Convert orders to protobuf response
            response_orders = [self._Order_to_response(order) for order in orders]
            
            return Order_pb2.ListOrderResponse(Orders=response_orders)


        except ValidationError as e:
            logger.error(f"Validation Error: {str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))

        except Exception as e:
            logger.error(f"Error listing orders: {str(e)} {str(traceback.format_exc())}")
            context.abort(grpc.StatusCode.INTERNAL, "Internal Server Error")    
        


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    Order_pb2_grpc.add_OrderServiceServicer_to_server(OrderService(),server)

    grpc_port = os.getenv('GRPC_SERVER_PORT', '50051')

    server.add_insecure_port(f"[::]:{grpc_port}")
    server.start()
    logger.info(f"Server Stated at {grpc_port}")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Stopping gRPC Server...")
        server.stop(0)


if __name__ == "__main__":
        
        """Starts the gRPC server."""
        try:
            logger.info("Starting gRPC server...")
            serve()
        except Exception as e:
            logger.error(f"Error in gRPC server: {e}")
