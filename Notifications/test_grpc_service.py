import unittest
import grpc
import sys
import os
from datetime import datetime, timedelta
from google.protobuf.timestamp_pb2 import Timestamp
import django
# Add the parent directory to sys.path to import the proto modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Notifications.settings')
django.setup()



import proto.Template_pb2 as template_pb2
import proto.Template_pb2_grpc as template_pb2_grpc
import proto.Messages_pb2 as message_pb2
import proto.Messages_pb2_grpc as message_pb2_grpc

class TestGRPCServices(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a gRPC channel
        cls.channel = grpc.insecure_channel('localhost:50051')
        
        # Create stubs for both services
        cls.template_stub = template_pb2_grpc.TemplateServiceStub(cls.channel)
        cls.message_stub = message_pb2_grpc.MessageServiceStub(cls.channel)

    @classmethod
    def tearDownClass(cls):
        cls.channel.close()

    def test_add_message_event(self):
        # Create a message event request
        variables = message_pb2.Variables(variables={
            "name": "John Doe",
            "amount": "100.00"
        })
        
        recipient = message_pb2.Recipient(
            to_number="+1234567890",
            from_number="+0987654321"
        )
        
        message_event = message_pb2.MessageEvent(
            template_name="test_template",
            variables=variables,
            recipient=recipient
        )
        
        request = message_pb2.AddMessageEventRequest(message_event=message_event)

        # Make the request
        response = self.message_stub.AddMessageEvent(request)

        # Assert the response
        self.assertTrue(response.success)
        self.assertIsNotNone(response.message)
        self.assertIsNone(response.error)

    def test_get_message_event(self):
        # First add a message event
        variables = message_pb2.Variables(variables={"test": "value"})
        recipient = message_pb2.Recipient(
            to_number="+1234567890",
            from_number="+0987654321"
        )
        message_event = message_pb2.MessageEvent(
            template_name="test_template",
            variables=variables,
            recipient=recipient
        )
        add_response = self.message_stub.AddMessageEvent(
            message_pb2.AddMessageEventRequest(message_event=message_event)
        )

        # Now try to get it
        get_request = message_pb2.GetMessageEventRequest(
            message_id=add_response.message.id
        )
        get_response = self.message_stub.GetMessageEvent(get_request)

        # Assert the response
        self.assertTrue(get_response.success)
        self.assertEqual(get_response.message.id, add_response.message.id)

    def test_list_messages(self):
        # Create a list messages request
        request = message_pb2.ListMessagesRequest(
            page=1,
            limit=10,
            template_name="test_template",
            status="PENDING"  # Use appropriate status from your enum
        )

        # Make the request
        response = self.message_stub.ListMessages(request)

        # Assert the response contains a list of messages
        self.assertIsInstance(response.messages, list)

    def test_invalid_message_id(self):
        # Try to get a message with an invalid ID
        request = message_pb2.GetMessageEventRequest(
            message_id="invalid_id"
        )

        # Assert that it raises an appropriate error
        with self.assertRaises(grpc.RpcError) as context:
            self.message_stub.GetMessageEvent(request)

        # Check if it's the expected error type
        self.assertEqual(context.exception.code(), grpc.StatusCode.NOT_FOUND)

    def test_update_message_event(self):
        # First create a message
        variables = message_pb2.Variables(variables={"test": "value"})
        recipient = message_pb2.Recipient(
            to_number="+1234567890",
            from_number="+0987654321"
        )
        message_event = message_pb2.MessageEvent(
            template_name="test_template",
            variables=variables,
            recipient=recipient
        )
        add_response = self.message_stub.AddMessageEvent(
            message_pb2.AddMessageEventRequest(message_event=message_event)
        )

        # Update the message
        updated_variables = message_pb2.Variables(variables={"test": "updated_value"})
        updated_recipient = message_pb2.Recipient(
            to_number="+9876543210",
            from_number="+0987654321"
        )
        updated_message_event = message_pb2.MessageEvent(
            template_name="test_template",
            variables=updated_variables,
            recipient=updated_recipient
        )

        update_request = message_pb2.UpdateMessageEventRequest(
            message_id=add_response.message.id,
            message_event=updated_message_event
        )

        update_response = self.message_stub.UpdateMessageEvent(update_request)

        # Assert the update was successful
        self.assertTrue(update_response.success)
        self.assertEqual(update_response.message.to_phone_number, "+9876543210")

if __name__ == '__main__':
    unittest.main() 