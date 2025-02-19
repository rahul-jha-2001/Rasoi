import os
import sys 
import django
from django.apps import apps
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from google.protobuf.timestamp_pb2 import Timestamp

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Notifications.settings')
django.setup()

from template.models import Template, Component, Parameters, Button
from message_service.models import Message,InvalidMessage
from utils.logger import Logger
# from utils.datetime_helpers import proto_to_django, django_to_proto, now_proto
logger = Logger("grpc_service")

import grpc
from concurrent import futures
import proto.Template_pb2 as template_pb2
import proto.Template_pb2_grpc as template_pb2_grpc
import proto.Messages_pb2 as message_pb2
import proto.Messages_pb2_grpc as message_pb2_grpc
from google.protobuf.empty_pb2 import Empty

from proto.Template_pb2 import (
    TemplateCategory, 
    TemplateStatus, 
    TemplateParameterFormat,
    TemplateComponentType,
    TemplateParameterType,
    TemplateButtonType
)

from proto.Messages_pb2 import (
    MessageStatus,
    MessagePriority
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
            return template_pb2.GetTemplateResponse(
                template={},
                success=False,
                error=template_pb2.Error(error="Invalid protobuf request format", error_code="INVALID_FORMAT")
            )

        try:
            if request.id:
                template = Template.objects.get_template_by_id(request.id)
                response = template_pb2.GetTemplateResponse(
                    template=self._template_to_proto(template),
                    success=True,
                    error=template_pb2.Error(error="", error_code="")
                )
            elif request.name:
                template = Template.objects.get_template_by_name(request.name)
                response = template_pb2.GetTemplateResponse(
                    template=self._template_to_proto(template),
                    success=True,
                    error=template_pb2.Error(error="", error_code="")
                )
            elif request.whatsapp_template_id:
                template = Template.objects.get_template_by_whatsapp_id(request.whatsapp_template_id)
                response = template_pb2.GetTemplateResponse(
                    template=self._template_to_proto(template),
                    success=True,
                    error=template_pb2.Error(error="", error_code="")
                )
            else:
                response = template_pb2.GetTemplateResponse(
                    template={},
                    success=False,
                    error=template_pb2.Error(error="Invalid request", error_code="INVALID_REQUEST")
                )

            return response

        except Template.DoesNotExist:
            logger.error(f"Template not found: {request}")
            return template_pb2.GetTemplateResponse(
                template={},
                success=False,
                error=template_pb2.Error(error="Template not found", error_code="NOT_FOUND")
            )
        except Exception as e:
            logger.error(f"Error getting template: {request}")
            return template_pb2.GetTemplateResponse(
                template={},
                success=False,
                error=template_pb2.Error(error=str(e), error_code="INTERNAL_ERROR")
            )

    def listTemplates(self, request, context):
        logger.info(f"Listing templates: {request}")

        # Verify incoming request
        if not self._verify_wire_format(request, template_pb2.ListTemplatesRequest):
            return template_pb2.ListTemplatesResponse(
                templates=[],
                next_page=0,
                previous_page=0,
                error=template_pb2.Error(error="Invalid protobuf request format", error_code="INVALID_FORMAT")
            )

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
                previous_page=previous_page,
                success=True,
                error=template_pb2.Error(error="", error_code="")
            )
            
            # Verify outgoing response
            if not self._verify_wire_format(response, template_pb2.ListTemplatesResponse):
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, "Failed to serialize response")

            return response

        except Exception as e:
            logger.error(f"Error listing templates: {request}")
            return template_pb2.ListTemplatesResponse(
                templates=[],
                next_page=0,
                previous_page=0,
                error=template_pb2.Error(error=str(e), error_code="INTERNAL_ERROR")
            )

class MessageService(message_pb2_grpc.MessageServiceServicer):

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
            # logger.debug(f"Serialized message size: {len(serialized)} bytes")
            # logger.debug(f"Message before serialization: {message}")
            
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

    def _message_to_proto(self, message: Message|None) -> message_pb2.Message:
        if message is None:
            return message_pb2.Message()
        else:
            proto_message = message_pb2.Message(
                id=str(message.id),
                to_phone_number=message.to_phone_number,
                from_phone_number=message.from_phone_number,
                template_name=message.template.name,
                status=MessageStatus.Value(message.status),
            message_type=MessagePriority.Value(message.message_type),
            message_json=str(message.message_json),
            rendered_message=str(message.rendered_message),
            variables=str(message.variables),
            created_at=message.created_at,
            updated_at=message.updated_at,
            sent_at=message.sent_at,
            error_message=message.error_message
        )
        if not self._verify_wire_format(proto_message, message_pb2.Message, f"message_id={message.id}"):
            raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize message {message.id}")
        return proto_message

    # def _short_message_to_proto(self, message: Message|None) -> message_pb2.ShortMessage:
    #     if message == None:
    #         return message_pb2.ShortMessage()
    #     else:
    #         proto_short_message = message_pb2.ShortMessage(
    #             id=str(message.id),
    #             to_phone_number=message.to_phone_number,
    #         from_phone_number=message.from_phone_number,
    #         template_name=message.template.name,
    #         # Fix: Use direct enum value instead of .get()
    #         status=MessageStatus.Value(message.status),
    #         message_type=MessagePriority.Value(message.message_type),
    #         created_at=message.created_at,
    #         updated_at=message.updated_at,
    #         sent_at=message.sent_at
    #     )
    #     if not self._verify_wire_format(proto_short_message, message_pb2.ShortMessage, f"message_id={message.id}"):
    #         raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize short message {message.id}")
    #     return proto_short_message

    def _invalid_message_to_proto(self, invalid_message: InvalidMessage|None) -> message_pb2.InvalidMessageEvent:
        if invalid_message is None:
            return message_pb2.InvalidMessageEvent()
        else:
            proto_invalid_message = message_pb2.InvalidMessageEvent(
                id=str(invalid_message.id),

                to_phone_number=invalid_message.to_phone_number,
                
                from_phone_number=invalid_message.from_phone_number,
                
                template=invalid_message.template.name,
                
                message_json=str(invalid_message.message_json),
                
                rendered_message=str(invalid_message.rendered_message),
                
                variables=str(invalid_message.variables),
                
                error_message=invalid_message.error_message,
                
                created_at=invalid_message.created_at,
                
                updated_at=invalid_message.updated_at
            )
            if not self._verify_wire_format(proto_invalid_message, message_pb2.InvalidMessageEvent, f"invalid_message_id={invalid_message.id}"):
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize invalid message {invalid_message.id}")
            return proto_invalid_message

    def AddMessageEvent(self, request, context):
        logger.info(f"Adding message event: {request.message_event.template_name}")

        
        if not self._verify_wire_format(request, message_pb2.AddMessageEventRequest):
            logger.error(f"Invalid protobuf request format: {request}")
            return message_pb2.AddMessageEventResponse(
                message={},
                success=False,
                error=message_pb2.Error(error="Invalid protobuf request format", error_code="INVALID_FORMAT")
            )
            
        try:
            message_event = Message.objects.create_message(
                template_name=request.message_event.template_name,
                variables=dict(request.message_event.variables.variables),
                to_phone_number=request.message_event.recipient.to_number,
                from_phone_number=request.message_event.recipient.from_number
            )
        except Exception as e:
            logger.error(f"Failed to create message event: {request.message_event.template_name}")
            return message_pb2.AddMessageEventResponse(
                message={},
                success=False,
                error=message_pb2.Error(error=str(e), error_code="CREATE_FAILED")
            )
        
        if message_event is None:
            logger.error(f"Invalid message Data {request.message_event.template_name}")
            return message_pb2.AddMessageEventResponse(
                message={},
                success=False,
                error=message_pb2.Error(error="Invalid message Data", error_code="INVALID_DATA")
            )
            
        response = message_pb2.AddMessageEventResponse(
            message=self._message_to_proto(message_event),
            success=True,
            error=message_pb2.Error(error="", error_code="")
        )
        
        logger.info(f"Message event added: {response.message.id}")
        if not self._verify_wire_format(response, message_pb2.AddMessageEventResponse):
            logger.error(f"Failed to serialize response: {response}")
            return message_pb2.AddMessageEventResponse(
                message={},
                success=False,
                error=message_pb2.Error(error="Failed to serialize response", error_code="SERIALIZATION_ERROR")
            )
            
        return response
    
    def UpdateMessageEvent(self, request, context):
        logger.info(f"Updating message event: {request.message_id}")
        if not self._verify_wire_format(request, message_pb2.UpdateMessageEventRequest):
            logger.error(f"Invalid protobuf request format: {request.message_id}")
            return message_pb2.UpdateMessageEventResponse(success=False, error="Invalid protobuf request format")
        try:
            message_event = Message.objects.update_message(
                message_id=request.message_id,
                variables=dict(request.message_event.variables.variables),
                to_phone_number=request.message_event.recipient.to_number,
                from_phone_number=request.message_event.recipient.from_number
            )
        except Exception as e:
            logger.error(f"Failed to update message event: {request.message_id}")
            return message_pb2.UpdateMessageEventResponse(message={}, success=False, error=message_pb2.Error(error=str(e), error_code="UPDATE_FAILED"))
        if message_event is None:
            logger.error(f"Invalid message Data {request.message_event.template_name}")
            return message_pb2.UpdateMessageEventResponse(message={}, success=False, error=message_pb2.Error(error="Invalid message Data", error_code="INVALID_DATA"))
        else:
            response = message_pb2.UpdateMessageEventResponse(
                message=self._message_to_proto(message_event),
                success=True,
                error=message_pb2.Error(error="", error_code="")
            )
        logger.info(f"Message event updated: {response.message.id}")
        if not self._verify_wire_format(response, message_pb2.UpdateMessageEventResponse):
            logger.error(f"Failed to serialize response: {response.message.idx}")
            return message_pb2.UpdateMessageEventResponse(message={}, success=False, error=message_pb2.Error(error="Failed to serialize response", error_code="SERIALIZATION_ERROR"))
        return response
    
    def RemoveMessageEvent(self, request, context):
        logger.info(f"Removing message event: {request.message_id}")
        if not self._verify_wire_format(request, message_pb2.RemoveMessageEventRequest):
            logger.error(f"Invalid protobuf request format: {request.message_id}")
            return message_pb2.RemoveMessageEventResponse(success=False, error=message_pb2.Error(error="Invalid protobuf request format", error_code="INVALID_FORMAT"))
        try:
           message = Message.objects.get(id=request.message_id)
        except Message.DoesNotExist:
            logger.error(f"Message not found: {request.message_id}")
            return message_pb2.RemoveMessageEventResponse(success=False, error=message_pb2.Error(error="Message not found", error_code="NOT_FOUND"))
        try:
            message.delete()
        except Exception as e:
            logger.error(f"Failed to delete message event: {request.message_id}")
            return message_pb2.RemoveMessageEventResponse(success=False, error=message_pb2.Error(error=str(e), error_code="DELETE_FAILED"))
        return message_pb2.RemoveMessageEventResponse(success=True, error=message_pb2.Error(error="", error_code=""))
    
    def GetMessageEvent(self, request, context):
        logger.info(f"Getting message event: {request}")
        if not self._verify_wire_format(request, message_pb2.GetMessageEventRequest):
            logger.error(f"Invalid protobuf request format: {request}")
            return message_pb2.GetMessageEventResponse(
                message={},
                success=False,
                error=message_pb2.Error(error="Invalid protobuf request format", error_code="INVALID_FORMAT")
            )
        try:
            message = Message.objects.get(id=request.message_id)
        except Message.DoesNotExist:
            logger.error(f"Message not found: {request.message_id}")
            return message_pb2.GetMessageEventResponse(
                message={},
                success=False,
                error=message_pb2.Error(error="Message not found", error_code="NOT_FOUND")
            )
        except Exception as e:
            logger.error(f"Error getting message event: {request.message_id} {str(e)}")
            return message_pb2.GetMessageEventResponse(
                message={},
                success=False,
                error=message_pb2.Error(error=str(e), error_code="INTERNAL_ERROR")
            )
        response = message_pb2.GetMessageEventResponse(
            message=self._message_to_proto(message),
            success=True,
            error=message_pb2.Error(error="", error_code="")
        )
        if not self._verify_wire_format(response, message_pb2.GetMessageEventResponse):
            logger.error(f"Failed to serialize response: {response}")
            return message_pb2.GetMessageEventResponse(
                message={},
                success=False,
                error=message_pb2.Error(error="Failed to serialize response", error_code="SERIALIZATION_ERROR")
            )
        return response
    
    def ListMessageEvents(self, request, context):
        logger.info(f"Listing message events: {request}")
        if not self._verify_wire_format(request, message_pb2.ListMessageEventRequest):
            logger.error(f"Invalid protobuf request format: {request}")
            return message_pb2.ListMessageEventResponse(success=False, error=message_pb2.Error(error="Invalid protobuf request format", error_code="INVALID_FORMAT"))
        
        try:    
            
            if request.HasField('start_date'):
                start_date = datetime.fromtimestamp(request.start_date.seconds + request.start_date.nanos/1e9, timezone.get_current_timezone())
            else:
                start_date = None
            if request.HasField('end_date'):
                end_date = datetime.fromtimestamp(request.end_date.seconds + request.end_date.nanos/1e9, timezone.get_current_timezone())
            else:
                end_date = None


            filters = {}
            # Add validated date filters
            if start_date:
                filters['created_at__gte'] = start_date
            if end_date:
                filters['created_at__lte'] = end_date

            # Add other filters only if explicitly set
            if request.HasField('template_name'):
                filters['template__name'] = request.template_name
            if request.HasField('to_phone_number'):
                filters['to_phone_number'] = request.to_phone_number
            if request.HasField('from_phone_number'):
                filters['from_phone_number'] = request.from_phone_number
            if request.HasField('message_category'):
                filters['message_type'] = TemplateCategory.Name(request.message_category)
            if request.HasField('status'):
                filters['status'] = request.status

            logger.debug(f"Filters: {filters}")
            messages, next_page, previous_page = Message.objects.get_messages_by_filter(
                page=request.page,
                limit=request.limit,
                **filters
            )
            
            response = message_pb2.ListMessageEventResponse(
                messages=[self._message_to_proto(message) for message in messages],
                next_page=next_page,
                previous_page=previous_page,
                success=True
            )
            
            if not self._verify_wire_format(response, message_pb2.ListMessageEventResponse):
                logger.error(f"Failed to serialize response: {response}")
                return message_pb2.ListMessageEventResponse(success=False, error=message_pb2.Error(error="Failed to serialize response", error_code="SERIALIZATION_ERROR"))
            return response

        except Exception as e:
            logger.error(f"Error listing message events: {str(e)}")
            return message_pb2.ListMessageEventResponse(
                success=False,
                error=message_pb2.Error(error=str(e), error_code="INTERNAL_ERROR")
            )


    def ListInvalidMessageEvents(self, request, context):
        logger.info(f"Listing Invalid Message Events: {request}")
        if not self._verify_wire_format(request, message_pb2.ListInvalidMessageEventRequest):
            logger.error(f"Invalid protobuf request format: {request}")
            return message_pb2.ListInvalidMessageEventResponse(
                invalid_messages=[],
                success=False,
                error=message_pb2.Error(error="Invalid protobuf request format", error_code="INVALID_FORMAT"),
                next_page=0,
                previous_page=0
            )
        
        try:    
            
            if request.HasField('start_date'):
                start_date = datetime.fromtimestamp(request.start_date.seconds + request.start_date.nanos/1e9, timezone.get_current_timezone())
            else:
                start_date = None
            if request.HasField('end_date'):
                end_date = datetime.fromtimestamp(request.end_date.seconds + request.end_date.nanos/1e9, timezone.get_current_timezone())
            else:
                end_date = None


            filters = {}
            # Add validated date filters
            if start_date:
                filters['created_at__gte'] = start_date
            if end_date:
                filters['created_at__lte'] = end_date

            # Add other filters only if explicitly set
            if request.HasField('template'):
                filters['template__name'] = request.template
            if request.HasField('to_phone_number'):
                filters['to_phone_number'] = request.to_phone_number
            if request.HasField('from_phone_number'):
                filters['from_phone_number'] = request.from_phone_number

            logger.debug(f"Filters: {filters}")
            messages, next_page, previous_page = InvalidMessage.objects.get_messages_by_filter(
                page=request.page,
                limit=request.limit,
                **filters
            )
            
            response = message_pb2.ListInvalidMessageEventResponse(
                invalid_messages=[self._invalid_message_to_proto(message) for message in messages],
                next_page=next_page,
                previous_page=previous_page,
                success=True
            )
            
            if not self._verify_wire_format(response, message_pb2.ListInvalidMessageEventResponse):
                logger.error(f"Failed to serialize response: {response}")
                return message_pb2.ListInvalidMessageEventResponse(
                    invalid_messages=[],
                    success=False,
                    error=message_pb2.Error(error="Failed to serialize response", error_code="SERIALIZATION_ERROR"),
                    next_page=0,
                    previous_page=0
                )
            return response

        except Exception as e:
            logger.error(f"Error listing invalid message events: {str(e)}")
            return message_pb2.ListInvalidMessageEventResponse(
                invalid_messages=[],
                success=False,
                error=message_pb2.Error(error=str(e), error_code="INTERNAL_ERROR"),
                next_page=0,
                previous_page=0
            )

    # def GetMessage(self, request, context):
    #     if not self._verify_wire_format(request, message_pb2.GetMessageRequest):
    #         logger.error(f"Invalid protobuf request format: {request}")
    #         return message_pb2.GetMessageResponse(message={},success=False, error=message_pb2.Error(error="Invalid protobuf request format", error_code="INVALID_FORMAT"))
    #     try:
    #         message = Message.objects.get(id=request.message_id)
    #     except Message.DoesNotExist:
    #         logger.error(f"Message not found: {request.message_id}")
    #         return message_pb2.GetMessageResponse(message={},success=False, error=message_pb2.Error(error="Message not found", error_code="NOT_FOUND"))
    #     response = message_pb2.GetMessageResponse(
    #         message=self._short_message_to_proto(message),
    #         success=True,
    #         error=message_pb2.Error(error="", error_code="")
    #     )
    #     if not self._verify_wire_format(response, message_pb2.GetMessageResponse):
    #         logger.error(f"Failed to serialize response: {response}")
    #         return message_pb2.GetMessageResponse(message={},success=False, error=message_pb2.Error(error="Failed to serialize response", error_code="SERIALIZATION_ERROR"))
    #     return response
    
    # def DeleteMessage(self, request, context):
    #     logger.info(f"Deleting message: {request.message_id}")
    #     if not self._verify_wire_format(request, message_pb2.DeleteMessageRequest):
    #         logger.error(f"Invalid protobuf request format: {request}")
    #         return message_pb2.DeleteMessageResponse(success=False, error=message_pb2.Error(error="Invalid protobuf request format", error_code="INVALID_FORMAT"))
    #     try:
    #         message = Message.objects.get(id=request.message_id)
    #     except Message.DoesNotExist:
    #         logger.error(f"Message not found: {request.message_id}")
    #         return message_pb2.DeleteMessageResponse(success=False, error=message_pb2.Error(error="Message not found", error_code="NOT_FOUND"))
    #     try:
    #         message.delete()
    #     except Exception as e:
    #         logger.error(f"Failed to delete message: {request.message_id}")
    #         return message_pb2.DeleteMessageResponse(success=False, error=message_pb2.Error(error=str(e), error_code="DELETE_FAILED"))
    #     return message_pb2.DeleteMessageResponse(success=True, error=message_pb2.Error(error="", error_code=""))
    
    # def ListMessages(self, request, context):
    #     logger.info(f"Listing messages: {request}")
    #     if not self._verify_wire_format(request, message_pb2.ListMessagesRequest):
    #         logger.error(f"Invalid protobuf request format: {request}")
    #         return message_pb2.ListMessagesResponse(success=False, error=message_pb2.Error(error="Invalid protobuf request format", error_code="INVALID_FORMAT"))
    #     try:
    #         messages, next_page, previous_page = Message.objects.get_messages_by_filter(
    #             page=request.page,
    #             limit=request.limit,
    #             template_name=request.template_name,
    #             to_phone_number=request.to_phone_number,
    #             from_phone_number=request.from_phone_number,
    #             message_category=request.message_category,
    #             status=request.status,
    #             start_date=request.start_date,
    #             end_date=request.end_date
    #         )
    #         response = message_pb2.ListMessagesResponse(
    #             messages=[self._short_message_to_proto(message) for message in messages],
    #             next_page=next_page,
    #             previous_page=previous_page
    #         )
    #         if not self._verify_wire_format(response, message_pb2.ListMessagesResponse):
    #             logger.error(f"Failed to serialize response: {response}")
    #             return message_pb2.ListMessagesResponse(success=False, error=message_pb2.Error(error="Failed to serialize response", error_code="SERIALIZATION_ERROR")      )
    #         return response
    #     except Exception as e:
    #         logger.error(f"Error listing messages: {request}")
    #         return message_pb2.ListMessagesResponse(success=False, error=message_pb2.Error(error=str(e), error_code="INTERNAL_ERROR"))

class Server:
    def __init__(self):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        template_pb2_grpc.add_TemplateServiceServicer_to_server(TemplateService(), self.server)
        message_pb2_grpc.add_MessageServiceServicer_to_server(MessageService(), self.server)
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