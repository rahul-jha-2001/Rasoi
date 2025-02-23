# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import Template_pb2 as Template__pb2

GRPC_GENERATED_VERSION = '1.70.0'
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
        + f' but the generated code in Template_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class TemplateServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.getTemplate = channel.unary_unary(
                '/template.v1.TemplateService/getTemplate',
                request_serializer=Template__pb2.GetTemplateRequest.SerializeToString,
                response_deserializer=Template__pb2.GetTemplateResponse.FromString,
                _registered_method=True)
        self.listTemplates = channel.unary_unary(
                '/template.v1.TemplateService/listTemplates',
                request_serializer=Template__pb2.ListTemplatesRequest.SerializeToString,
                response_deserializer=Template__pb2.ListTemplatesResponse.FromString,
                _registered_method=True)


class TemplateServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def getTemplate(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def listTemplates(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_TemplateServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'getTemplate': grpc.unary_unary_rpc_method_handler(
                    servicer.getTemplate,
                    request_deserializer=Template__pb2.GetTemplateRequest.FromString,
                    response_serializer=Template__pb2.GetTemplateResponse.SerializeToString,
            ),
            'listTemplates': grpc.unary_unary_rpc_method_handler(
                    servicer.listTemplates,
                    request_deserializer=Template__pb2.ListTemplatesRequest.FromString,
                    response_serializer=Template__pb2.ListTemplatesResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'template.v1.TemplateService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('template.v1.TemplateService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class TemplateService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def getTemplate(request,
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
            '/template.v1.TemplateService/getTemplate',
            Template__pb2.GetTemplateRequest.SerializeToString,
            Template__pb2.GetTemplateResponse.FromString,
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
    def listTemplates(request,
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
            '/template.v1.TemplateService/listTemplates',
            Template__pb2.ListTemplatesRequest.SerializeToString,
            Template__pb2.ListTemplatesResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
