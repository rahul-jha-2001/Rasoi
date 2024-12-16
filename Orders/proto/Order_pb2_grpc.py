# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import Order_pb2 as Order__pb2

GRPC_GENERATED_VERSION = '1.66.2'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in Order_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class OrderServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.CreateOrder = channel.unary_unary(
                '/Order_v1.OrderService/CreateOrder',
                request_serializer=Order__pb2.CreateOrderRequest.SerializeToString,
                response_deserializer=Order__pb2.OrderResponse.FromString,
                _registered_method=True)
        self.GetOrder = channel.unary_unary(
                '/Order_v1.OrderService/GetOrder',
                request_serializer=Order__pb2.GetOrderRequest.SerializeToString,
                response_deserializer=Order__pb2.OrderResponse.FromString,
                _registered_method=True)
        self.UpdateOrder = channel.unary_unary(
                '/Order_v1.OrderService/UpdateOrder',
                request_serializer=Order__pb2.UpdateOrderRequest.SerializeToString,
                response_deserializer=Order__pb2.OrderResponse.FromString,
                _registered_method=True)
        self.DeleteOrder = channel.unary_unary(
                '/Order_v1.OrderService/DeleteOrder',
                request_serializer=Order__pb2.DeleteOrderRequest.SerializeToString,
                response_deserializer=Order__pb2.empty.FromString,
                _registered_method=True)
        self.ListOrder = channel.unary_unary(
                '/Order_v1.OrderService/ListOrder',
                request_serializer=Order__pb2.ListOrderRequest.SerializeToString,
                response_deserializer=Order__pb2.ListOrderResponse.FromString,
                _registered_method=True)


class OrderServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def CreateOrder(self, request, context):
        """Core order service 
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetOrder(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateOrder(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteOrder(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListOrder(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_OrderServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'CreateOrder': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateOrder,
                    request_deserializer=Order__pb2.CreateOrderRequest.FromString,
                    response_serializer=Order__pb2.OrderResponse.SerializeToString,
            ),
            'GetOrder': grpc.unary_unary_rpc_method_handler(
                    servicer.GetOrder,
                    request_deserializer=Order__pb2.GetOrderRequest.FromString,
                    response_serializer=Order__pb2.OrderResponse.SerializeToString,
            ),
            'UpdateOrder': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateOrder,
                    request_deserializer=Order__pb2.UpdateOrderRequest.FromString,
                    response_serializer=Order__pb2.OrderResponse.SerializeToString,
            ),
            'DeleteOrder': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteOrder,
                    request_deserializer=Order__pb2.DeleteOrderRequest.FromString,
                    response_serializer=Order__pb2.empty.SerializeToString,
            ),
            'ListOrder': grpc.unary_unary_rpc_method_handler(
                    servicer.ListOrder,
                    request_deserializer=Order__pb2.ListOrderRequest.FromString,
                    response_serializer=Order__pb2.ListOrderResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Order_v1.OrderService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('Order_v1.OrderService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class OrderService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def CreateOrder(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/Order_v1.OrderService/CreateOrder',
            Order__pb2.CreateOrderRequest.SerializeToString,
            Order__pb2.OrderResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetOrder(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/Order_v1.OrderService/GetOrder',
            Order__pb2.GetOrderRequest.SerializeToString,
            Order__pb2.OrderResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def UpdateOrder(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/Order_v1.OrderService/UpdateOrder',
            Order__pb2.UpdateOrderRequest.SerializeToString,
            Order__pb2.OrderResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def DeleteOrder(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/Order_v1.OrderService/DeleteOrder',
            Order__pb2.DeleteOrderRequest.SerializeToString,
            Order__pb2.empty.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def ListOrder(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/Order_v1.OrderService/ListOrder',
            Order__pb2.ListOrderRequest.SerializeToString,
            Order__pb2.ListOrderResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)