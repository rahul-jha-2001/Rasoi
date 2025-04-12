import unittest
from unittest.mock import patch, MagicMock
from grpc import StatusCode
from Proto import order_pb2, order_pb2_grpc
from Orders.grpc_serve import OrderService, handle_error, check_access
from django.core.exceptions import ValidationError

class TestOrderService(unittest.TestCase):

    def setUp(self):
        self.service = OrderService()
        self.context = MagicMock()

    @patch("Orders.grpc_serve.Order.objects.get")
    def test_GetOrder_valid_order_uuid(self, mock_get_order):
        # Mock the order object
        mock_order = MagicMock()
        mock_order.order_uuid = "valid-order-uuid"
        mock_get_order.return_value = mock_order

        # Mock request
        request = MagicMock()
        request.store_uuid = "valid-store-uuid"
        request.order_uuid = "valid-order-uuid"

        # Call the method
        response = self.service.GetOrder(request, self.context)

        # Assertions
        self.assertEqual(response.order.order_uuid, "valid-order-uuid")
        mock_get_order.assert_called_once_with(order_uuid="valid-order-uuid", store_uuid="valid-store-uuid")

    @patch("Orders.grpc_serve.Order.objects.get")
    def test_GetOrder_invalid_order_uuid(self, mock_get_order):
        # Mock the order object to raise DoesNotExist
        mock_get_order.side_effect = Order.DoesNotExist

        # Mock request
        request = MagicMock()
        request.store_uuid = "valid-store-uuid"
        request.order_uuid = "invalid-order-uuid"

        # Call the method and assert exception
        with self.assertRaises(Exception):
            self.service.GetOrder(request, self.context)

    @patch("Orders.grpc_serve.Order.objects.get")
    def test_CancelOrder_valid_order(self, mock_get_order):
        # Mock the order object
        mock_order = MagicMock()
        mock_order.order_status = "ORDER_STATE_PLACED"
        mock_order.payment = MagicMock()
        mock_get_order.return_value = mock_order

        # Mock request
        request = MagicMock()
        request.store_uuid = "valid-store-uuid"
        request.order_uuid = "valid-order-uuid"

        # Call the method
        response = self.service.CancelOrder(request, self.context)

        # Assertions
        self.assertEqual(response.order.order_status, "ORDER_STATE_CANCELED")
        mock_get_order.assert_called_once_with(order_uuid="valid-order-uuid", store_uuid="valid-store-uuid")

    @patch("Orders.grpc_serve.Order.objects.get")
    def test_CancelOrder_invalid_order(self, mock_get_order):
        # Mock the order object to raise DoesNotExist
        mock_get_order.side_effect = Order.DoesNotExist

        # Mock request
        request = MagicMock()
        request.store_uuid = "valid-store-uuid"
        request.order_uuid = "invalid-order-uuid"

        # Call the method and assert exception
        with self.assertRaises(Exception):
            self.service.CancelOrder(request, self.context)

    @patch("Orders.grpc_serve.Order.objects.get")
    def test_UpdateOrderState_valid_order(self, mock_get_order):
        # Mock the order object
        mock_order = MagicMock()
        mock_get_order.return_value = mock_order

        # Mock request
        request = MagicMock()
        request.store_uuid = "valid-store-uuid"
        request.order_uuid = "valid-order-uuid"
        request.order_state = "ORDER_STATE_READY"

        # Call the method
        response = self.service.UpdateOrderState(request, self.context)

        # Assertions
        self.assertEqual(response.order.order_status, "ORDER_STATE_READY")
        mock_get_order.assert_called_once_with(order_uuid="valid-order-uuid", store_uuid="valid-store-uuid")

    @patch("Orders.grpc_serve.Order.objects.get_store_orders")
    def test_ListOrder(self, mock_get_store_orders):
        # Mock the orders
        mock_order = MagicMock()
        mock_get_store_orders.return_value = ([mock_order], None, None)

        # Mock request
        request = MagicMock()
        request.store_uuid = "valid-store-uuid"
        request.limit = 10
        request.page = 1

        # Call the method
        response = self.service.ListOrder(request, self.context)

        # Assertions
        self.assertEqual(len(response.orders), 1)
        mock_get_store_orders.assert_called_once_with(store_uuid="valid-store-uuid", limit=10, page=1)

    @patch("Orders.grpc_serve.Order.objects.get_user_orders")
    def test_listUserOrder(self, mock_get_user_orders):
        # Mock the orders
        mock_order = MagicMock()
        mock_get_user_orders.return_value = ([mock_order], None, None)

        # Mock request
        request = MagicMock()
        request.store_uuid = "valid-store-uuid"
        request.user_phone_no = "1234567890"
        request.limit = 10
        request.page = 1

        # Call the method
        response = self.service.listUserOrder(request, self.context)

        # Assertions
        self.assertEqual(len(response.orders), 1)
        mock_get_user_orders.assert_called_once_with(
            store_uuid="valid-store-uuid",
            user_phone_no="1234567890",
            limit=10,
            page=1
        )

    @patch("Orders.grpc_serve.Order.objects.get")
    def test_GetUserOrder_valid_order(self, mock_get_order):
        # Mock the order object
        mock_order = MagicMock()
        mock_order.order_uuid = "valid-order-uuid"
        mock_get_order.return_value = mock_order

        # Mock request
        request = MagicMock()
        request.user_phone_no = "1234567890"
        request.order_uuid = "valid-order-uuid"

        # Call the method
        response = self.service.GetUserOrder(request, self.context)

        # Assertions
        self.assertEqual(response.order.order_uuid, "valid-order-uuid")
        mock_get_order.assert_called_once_with(user_phone_no="1234567890", order_uuid="valid-order-uuid")

    @patch("Orders.grpc_serve.Order.objects.get")
    def test_CancelUserOrder_valid_order(self, mock_get_order):
        # Mock the order object
        mock_order = MagicMock()
        mock_order.order_status = "ORDER_STATE_PLACED"
        mock_order.payment = MagicMock()
        mock_get_order.return_value = mock_order

        # Mock request
        request = MagicMock()
        request.user_phone_no = "1234567890"
        request.order_uuid = "valid-order-uuid"

        # Call the method
        response = self.service.CancelUserOrder(request, self.context)

        # Assertions
        self.assertEqual(response.order.order_status, "ORDER_STATE_CANCELED")
        mock_get_order.assert_called_once_with(user_phone_no="1234567890", order_uuid="valid-order-uuid")


if __name__ == "__main__":
    unittest.main()