"""
Unit tests for Codex SMS Python SDK v0.2.0.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shanma import (
    ShanmaClient,
    CodexSmsClient,
    ActivationContext,
    OrderResult,
    SmsResult,
    normalize_service,
    ShanmaError,
    AuthenticationError,
    InsufficientBalanceError,
    UpstreamCarrierError,
    NumberUnavailableError,
)


class TestShanmaClient(unittest.TestCase):

    def test_brand_alias(self):
        """Test that CodexSmsClient is an alias for ShanmaClient."""
        self.assertIs(CodexSmsClient, ShanmaClient)
        client = CodexSmsClient(api_key="test_token")
        self.assertIsInstance(client, ShanmaClient)
        self.assertEqual(client.VERSION, "0.2.0")

    def test_init_without_key_raises_error(self):
        """Test initialization without API key raises AuthenticationError."""
        with self.assertRaises(AuthenticationError):
            ShanmaClient(api_key="")

        with self.assertRaises(AuthenticationError):
            ShanmaClient(api_key="   ")

    def test_normalize_service(self):
        """Test service aliases normalization."""
        self.assertEqual(normalize_service("chatgpt"), "openai")
        self.assertEqual(normalize_service("dr"), "openai")
        self.assertEqual(normalize_service("go"), "google")
        self.assertEqual(normalize_service("gmail"), "google")
        self.assertEqual(normalize_service("tg"), "telegram")
        self.assertEqual(normalize_service("wa"), "whatsapp")
        self.assertEqual(normalize_service("mm"), "microsoft")
        self.assertEqual(normalize_service("x"), "twitter")
        self.assertEqual(normalize_service("custom_unknown_svc"), "custom_unknown_svc")

    @patch("urllib.request.urlopen")
    def test_get_balance(self, mock_urlopen):
        """Test retrieving balance."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"balance": 45.50}).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client = ShanmaClient(api_key="mock_key")
        balance = client.get_balance()
        self.assertEqual(balance, 45.50)

    @patch("urllib.request.urlopen")
    def test_order_number_success(self, mock_urlopen):
        """Test ordering a virtual number successfully with alias normalization."""
        mock_payload = {
            "success": True,
            "activation_id": "act_998822",
            "phone_number": "+12025550199"
        }
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_payload).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client = ShanmaClient(api_key="mock_key")
        # Pass alias 'chatgpt', should normalize to 'openai'
        order = client.order_number(service="chatgpt", country="usa")

        self.assertIsInstance(order, OrderResult)
        self.assertEqual(order.activation_id, "act_998822")
        self.assertEqual(order.phone_number, "+12025550199")
        self.assertEqual(order.service, "openai")
        self.assertEqual(order.country, "usa")

    @patch("urllib.request.urlopen")
    def test_order_number_insufficient_balance(self, mock_urlopen):
        """Test ordering a virtual number when balance is insufficient."""
        mock_payload = {
            "success": False,
            "message": "Insufficient balance. Please recharge."
        }
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_payload).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client = ShanmaClient(api_key="mock_key")
        with self.assertRaises(InsufficientBalanceError):
            client.order_number(service="openai", country="usa")

    @patch("urllib.request.urlopen")
    def test_order_number_out_of_stock(self, mock_urlopen):
        """Test ordering when no numbers are available."""
        mock_payload = {
            "success": False,
            "message": "Out of stock. No numbers available."
        }
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_payload).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client = ShanmaClient(api_key="mock_key")
        with self.assertRaises(NumberUnavailableError):
            client.order_number(service="openai", country="usa")

    @patch("urllib.request.urlopen")
    def test_query_sms_received(self, mock_urlopen):
        """Test querying SMS when code has arrived."""
        mock_payload = {
            "status": "received",
            "sms_code": "847291",
            "sms_text": "Your verification code is 847291."
        }
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_payload).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client = ShanmaClient(api_key="mock_key")
        res = client.query_sms("act_998822")

        self.assertIsNotNone(res)
        self.assertEqual(res.code, "847291")
        self.assertIn("847291", res.full_text)

    @patch("urllib.request.urlopen")
    def test_cancel_order(self, mock_urlopen):
        """Test cancelling an order."""
        mock_payload = {"success": True}
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_payload).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client = ShanmaClient(api_key="mock_key")
        ok = client.cancel_order("act_998822")
        self.assertTrue(ok)

    @patch("urllib.request.urlopen")
    def test_wait_for_sms_with_callback(self, mock_urlopen):
        """Test wait_for_sms with on_poll callback."""
        mock_response = MagicMock()
        # Returns SMS on first attempt
        mock_response.read.return_value = json.dumps({
            "status": "received",
            "sms_code": "123456",
            "sms_text": "Code: 123456"
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        polls = []
        def poll_callback(attempt, elapsed):
            polls.append((attempt, elapsed))

        client = ShanmaClient(api_key="mock_key")
        res = client.wait_for_sms("act_998822", timeout=10, interval=1, on_poll=poll_callback)
        self.assertIsNotNone(res)
        self.assertEqual(res.code, "123456")
        self.assertEqual(len(polls), 1)

    @patch.object(ShanmaClient, "cancel_order")
    @patch.object(ShanmaClient, "order_number")
    def test_activation_context_auto_cancel_on_no_sms(self, mock_order, mock_cancel):
        """Test that ActivationContext auto-cancels order if no SMS is received."""
        mock_order.return_value = OrderResult(
            activation_id="act_ctx_1",
            phone_number="+10000000",
            service="openai",
            country="usa",
            raw={}
        )
        mock_cancel.return_value = True

        client = ShanmaClient(api_key="mock_key")
        with patch.object(ShanmaClient, "wait_for_sms", return_value=None):
            with client.activation(service="openai", country="usa", auto_cancel=True) as act:
                sms = act.wait_for_sms(timeout=1)
                self.assertIsNone(sms)

        mock_cancel.assert_called_once_with("act_ctx_1")


if __name__ == "__main__":
    unittest.main()
