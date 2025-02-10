import os
import sys 
import django
from django.apps import apps
from django.db import transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Notifications.settings')
django.setup()

from template.models import Template, Component, Parameters, Button
from utils.logger import Logger

logger = Logger("grpc_service")

import grpc
from concurrent import futures
import proto.Template_pb2 as template_pb2
import proto.Template_pb2_grpc as template_pb2_grpc
from proto.Template_pb2 import (
    TemplateCategory, 
    TemplateStatus, 
    TemplateParameterFormat,
    TemplateComponentType,
    TemplateParameterType,
    TemplateButtonType
)

# Category mappings
CATEGORY_MAP = {
    'MARKETING': TemplateCategory.MARKETING,
    'UTILITY': TemplateCategory.UTILITY,
    'AUTHENTICATION': TemplateCategory.AUTHENTICATION
}

# Status mappings
STATUS_MAP = {
    'PENDING': TemplateStatus.PENDING,
    'APPROVED': TemplateStatus.APPROVED,
    'REJECTED': TemplateStatus.REJECTED
}

# Parameter format mappings
PARAMETER_FORMAT_MAP = {
    'POSITIONAL': TemplateParameterFormat.POSITIONAL,
    'NAMED': TemplateParameterFormat.NAMED
}

# Component type mappings
COMPONENT_TYPE_MAP = {
    'HEADER': TemplateComponentType.HEADER,
    'BODY': TemplateComponentType.BODY,
    'FOOTER': TemplateComponentType.FOOTER
}

# Parameter type mappings
PARAMETER_TYPE_MAP = {
    'TEXT': TemplateParameterType.TEXT,
    'CURRENCY': TemplateParameterType.CURRENCY,
    'MEDIA': TemplateParameterType.MEDIA
}

# Button type mappings
BUTTON_TYPE_MAP = {
    'QUICK_REPLY': TemplateButtonType.QUICK_REPLY,
    'URL': TemplateButtonType.URL
}

class TemplateService(template_pb2_grpc.TemplateServiceServicer):
    def _verify_wire_format(self, message, message_type, context_info=""):
        """Helper to verify protobuf wire format
        Args:
            message: The protobuf message to verify
            message_type: The protobuf message class type
            context_info: Additional context for logging
        Returns:
            bool: True if verification succeeds
        """
        try:
            serialized = message.SerializeToString()
            logger.debug(f"Serialized message size: {len(serialized)} bytes")
            logger.debug(f"Message before serialization: {message}")
            
            test_msg = message_type()
            test_msg.ParseFromString(serialized)
            
            # Compare fields before and after serialization
            original_fields = message.ListFields()
            test_fields = test_msg.ListFields()
            
            if len(original_fields) != len(test_fields):
                logger.error(f"Field count mismatch - Original: {len(original_fields)}, Deserialized: {len(test_fields)}")
                logger.error(f"Original fields: {[f[0].name for f in original_fields]}")
                logger.error(f"Deserialized fields: {[f[0].name for f in test_fields]}")
            
            return True
        except Exception as e:
            logger.error(f"Wire format verification failed for {message_type.__name__} {context_info}: {str(e)}")
            logger.error(f"Message contents: {message}")
            # Print hex dump of serialized data if available
            try:
                logger.error(f"Serialized hex: {serialized.hex()}")
            except:
                pass
            return False

    def _parameter_to_proto(self, parameter: Parameters) -> template_pb2.TemplateParameter:
        proto_param = template_pb2.TemplateParameter(
            name=str(parameter.name),
            type=PARAMETER_TYPE_MAP.get(parameter.type),
            text_value=str(parameter.text_value),
            index=parameter.index
        )
        if not self._verify_wire_format(proto_param, template_pb2.TemplateParameter, f"parameter_id={parameter.id}"):
            raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize parameter {parameter.id}")
        return proto_param

    def _button_to_proto(self, button: Button) -> template_pb2.TemplateButton:
        proto_button = template_pb2.TemplateButton(
            type=BUTTON_TYPE_MAP.get(button.type),
            text=str(button.text),
            url=str(button.url) if button.url else None,
            index=button.index
        )
        if not self._verify_wire_format(proto_button, template_pb2.TemplateButton, f"button_id={button.id}"):
            raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize button {button.id}")
        return proto_button

    def _component_to_proto(self, component: Component) -> template_pb2.TemplateComponent:
        proto_component = template_pb2.TemplateComponent(
            type=COMPONENT_TYPE_MAP.get(component.type),
            text=str(component.text),
            format=str(component.format) if component.format else None,
            parameters=[self._parameter_to_proto(parameter) for parameter in component.parameters.all()]
        )
        if not self._verify_wire_format(proto_component, template_pb2.TemplateComponent, f"component_id={component.id}"):
            raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize component {component.id}")
        return proto_component

    def _template_to_proto(self, template: Template) -> template_pb2.Template:
        try:
            proto_template = template_pb2.Template(
                id=str(template.id),
                name=str(template.name),
                category=CATEGORY_MAP.get(template.category),
                status=STATUS_MAP.get(template.status),
                language=str(template.language),
                parameter_format=PARAMETER_FORMAT_MAP.get(template.parameter_format),
                message_send_ttl_seconds=template.message_send_ttl_seconds,
                whatsapp_template_id=str(template.whatsapp_template_id),
                components=[self._component_to_proto(component) for component in template.components.all()],
                buttons=[self._button_to_proto(button) for button in template.buttons.all()]
            )
            if not self._verify_wire_format(proto_template, template_pb2.Template, f"template_id={template.id}"):
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize template {template.id}")
            return proto_template
        except Exception as e:
            logger.error(f"Failed to create template proto for {template.id}: {str(e)}")
            raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize template: {str(e)}")

    def getTemplate(self, request, context):
        logger.info(f"Getting template: {request}")
        
        # Verify incoming request
        if not self._verify_wire_format(request, template_pb2.GetTemplateRequest):
            raise grpc.RpcError(grpc.StatusCode.INVALID_ARGUMENT, "Invalid protobuf request format")

        try:
            if request.id:
                template = Template.objects.get_template_by_id(request.id)
                response = template_pb2.GetTemplateResponse(
                    template=self._template_to_proto(template)
                )
            elif request.name:
                template = Template.objects.get_template_by_name(request.name)
                response = template_pb2.GetTemplateResponse(
                    template=self._template_to_proto(template)
                )
            elif request.whatsapp_template_id:
                template = Template.objects.get_template_by_whatsapp_id(request.whatsapp_template_id)
                response = template_pb2.GetTemplateResponse(
                    template=self._template_to_proto(template)
                )
            else:
                raise grpc.RpcError(grpc.StatusCode.INVALID_ARGUMENT, f"Invalid request")

            # Verify outgoing response
            if not self._verify_wire_format(response, template_pb2.GetTemplateResponse):
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, "Failed to serialize response")
            return response

        except Template.DoesNotExist:
            logger.error(f"Template not found: {request}")
            raise grpc.RpcError(grpc.StatusCode.NOT_FOUND, f"Template not found")
        except Exception as e:
            logger.error(f"Error getting template: {request}")
            raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Error getting template: {e}")

    def listTemplates(self, request, context):
        logger.info(f"Listing templates: {request}")

        # Verify incoming request
        if not self._verify_wire_format(request, template_pb2.ListTemplatesRequest):
            raise grpc.RpcError(grpc.StatusCode.INVALID_ARGUMENT, "Invalid protobuf request format")

        try:
            templates, next_page, previous_page = Template.objects.get_templates_by_filter(
                category=request.category,
                status=request.status,
                language=request.language,
                parameter_format=request.parameter_format,
                page=request.page,
                limit=request.limit
            )
            response = template_pb2.ListTemplatesResponse(
                templates=[self._template_to_proto(template) for template in templates],
                next_page=next_page,
                previous_page=previous_page
            )
            
            # Verify outgoing response
            if not self._verify_wire_format(response, template_pb2.ListTemplatesResponse):
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, "Failed to serialize response")
            return response

        except Exception as e:
            logger.error(f"Error listing templates: {request}")
            raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Error listing templates: {e}")

class Server:
    def __init__(self):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        template_pb2_grpc.add_TemplateServiceServicer_to_server(TemplateService(), self.server)
        self.server.add_insecure_port('localhost:50051')
        self.server.start()
        logger.info(f"Server started on port 50051")

    def run(self):
        self.server.wait_for_termination()

    def stop(self):
        self.server.stop(0)

if __name__ == '__main__':
    server = Server()
    server.run()
    server.stop()