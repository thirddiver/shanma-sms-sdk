"""
Unit tests for Codex SMS (ShanMa) Python SDK.
"""

import unittest
from unittest.mock import patch, MagicMock
import io
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shanma import (
    ShanmaClient,
    CodexSmsClient,
    OrderResult,
    SmsResult,
    ShanmaError,
    AuthenticationError,
    InsufficientBalanceError,
    UpstreamCarrierError
)

class TestShanmaClient(unittest.TestCase):

    def test_brand_alias(self):
        """Test that CodexSmsClient is an alias for ShanmaClient."""
        self.assertIs(CodexSmsClient, ShanmaClient)
        client = CodexSmsClient(api_key="test_token")
        self.assertIsInstance(client, ShanmaClient)

    def test_init_without_key_raises_error(self):
        """Test initialization without API key raises AuthenticationError."""
        with self.assertRaises(AuthenticationError):
            ShanmaClient(api_key="")

        with self.assertRaises(AuthenticationError):
            ShanmaClient(api_key="   ")

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
        """Test ordering a virtual number successfully."""
        mock_payload = {
            "success": True,
            "activation_id": "act_998822",
            "phone_number": "+12025550199"
        }
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_payload).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client = ShanmaClient(api_key="mock_key")
        order = client.order_number(service="openai", country="usa")

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

if __name__ == "__main__":
    unittest.main()
