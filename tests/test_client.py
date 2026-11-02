"""
Unit tests for Codex SMS Python SDK v0.3.1.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os
import urllib.error

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shanma import (
    CodexSmsClient,
    ShanmaClient,
    ActivationContext,
    OrderResult,
    SmsResult,
    normalize_service,
    CodexSmsError,
    ShanmaError,
    AuthenticationError,
    RateLimitError,
    CdkAlreadyUsedError,
    ActivationNotFoundError,
    NumberUnavailableError,
)


class TestCodexSmsClient(unittest.TestCase):

    def test_brand_alias(self):
        """Test that ShanmaClient is an alias for CodexSmsClient and CodexSmsError is ShanmaError."""
        self.assertIs(ShanmaClient, CodexSmsClient)
        self.assertIs(CodexSmsError, ShanmaError)
        client = CodexSmsClient(cdkey="test_cdk")
        self.assertIsInstance(client, CodexSmsClient)
        self.assertEqual(client.VERSION, "0.3.1")
        self.assertEqual(client.cdkey, "test_cdk")
        self.assertEqual(client.api_key, "test_cdk")

    def test_init_without_key_raises_error(self):
        """Test initialization without CDK raises AuthenticationError."""
        with self.assertRaises(AuthenticationError):
            CodexSmsClient(cdkey="")

        with self.assertRaises(AuthenticationError):
            CodexSmsClient(cdkey="   ")

        with self.assertRaises(AuthenticationError):
            CodexSmsClient(api_key="")

    def test_init_with_api_key_alias(self):
        """Test backwards compatibility for initializing with api_key argument."""
        client = CodexSmsClient(api_key="cdk_via_api_key")
        self.assertEqual(client.cdkey, "cdk_via_api_key")

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
        self.assertIsNone(normalize_service(None))

    @patch("urllib.request.urlopen")
    def test_redeem_success(self, mock_urlopen):
        """Test redeeming a CDK allocates a phone number with Bearer auth and strict empty body."""
        mock_payload = {
            "code": "CDK_TEST_123",
            "phone": "+12025550199",
            "activation_id": "act_889900",
            "service": "openai",
            "country_name": "United States",
            "can_resend": False,
        }
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_payload).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client = CodexSmsClient(cdkey="CDK_TEST_123")
        order = client.redeem(service="chatgpt")

        self.assertIsInstance(order, OrderResult)
        self.assertEqual(order.phone_number, "+12025550199")
        self.assertEqual(order.activation_id, "act_889900")
        self.assertEqual(order.service, "openai")
        self.assertEqual(order.country, "United States")

        # Verify HTTP request headers & wire protocol conformance: body must be {} (extra=forbid in backend)
        args, kwargs = mock_urlopen.call_args
        req = args[0]
        self.assertEqual(req.full_url, "https://shanma.store/api/guest/cdkeys/redeem")
        self.assertEqual(req.headers.get("Authorization"), "Bearer CDK_TEST_123")
        self.assertEqual(req.headers.get("Content-type"), "application/json")
        sent_body = json.loads(req.data.decode("utf-8"))
        self.assertEqual(sent_body, {})

    @patch("urllib.request.urlopen")
    def test_get_status(self, mock_urlopen):
        """Test retrieving CDK status without consuming operations."""
        mock_payload = {
            "code": "CDK_TEST_123",
            "status": "bound",
            "phone": "+12025550199",
            "activation_id": "act_889900",
            "service": "openai",
        }
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_payload).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client = CodexSmsClient(cdkey="CDK_TEST_123")
        status = client.get_status()
        self.assertEqual(status["status"], "bound")
        self.assertEqual(status["phone"], "+12025550199")

    @patch("urllib.request.urlopen")
    def test_query_sms_waiting_and_received(self, mock_urlopen):
        """Test querying SMS during waiting and after received."""
        client = CodexSmsClient(cdkey="CDK_TEST_123")

        # Case 1: Still waiting
        mock_waiting = MagicMock()
        mock_waiting.read.return_value = json.dumps({"status": "waiting"}).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_waiting
        res_waiting = client.query_sms()
        self.assertIsNone(res_waiting)

        # Case 2: Code received
        mock_received = MagicMock()
        mock_received.read.return_value = json.dumps({
            "status": "received",
            "code": "654321",
            "text": "Your OpenAI verification code is 654321.",
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_received
        res_received = client.query_sms()
        self.assertIsInstance(res_received, SmsResult)
        self.assertEqual(res_received.code, "654321")
        self.assertIn("654321", res_received.full_text)

    @patch("urllib.request.urlopen")
    def test_switch_phone(self, mock_urlopen):
        """Test switching phone number if banned or unreceived."""
        mock_payload = {
            "code": "CDK_TEST_123",
            "phone": "+447911123456",
            "activation_id": "act_new_99",
            "service": "openai",
            "country_name": "United Kingdom",
        }
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_payload).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client = CodexSmsClient(cdkey="CDK_TEST_123")
        new_order = client.switch_phone()

        self.assertIsInstance(new_order, OrderResult)
        self.assertEqual(new_order.phone_number, "+447911123456")
        self.assertEqual(new_order.activation_id, "act_new_99")
        self.assertEqual(new_order.country, "United Kingdom")

    @patch("urllib.request.urlopen")
    def test_wait_for_sms_with_callback(self, mock_urlopen):
        """Test wait_for_sms with on_poll callback."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "status": "received",
            "code": "999888",
            "text": "Code: 999888",
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        polls = []
        def poll_callback(attempt, elapsed):
            polls.append((attempt, elapsed))

        client = CodexSmsClient(cdkey="CDK_TEST_123")
        res = client.wait_for_sms(timeout=10, interval=4, on_poll=poll_callback)
        self.assertIsNotNone(res)
        self.assertEqual(res.code, "999888")
        self.assertEqual(len(polls), 1)

    @patch("urllib.request.urlopen")
    def test_http_error_mappings(self, mock_urlopen):
        """Test accurate HTTP error translation to typed exceptions."""
        client = CodexSmsClient(cdkey="CDK_TEST_123")

        # 401 / 403 AuthenticationError
        err_401 = urllib.error.HTTPError(
            url="https://shanma.store/api/guest/cdkeys/redeem",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=MagicMock(read=lambda: b'{"detail":"Invalid CDK"}')
        )
        mock_urlopen.side_effect = err_401
        with self.assertRaises(AuthenticationError):
            client.redeem()

        # 404 ActivationNotFoundError
        err_404 = urllib.error.HTTPError(
            url="https://shanma.store/api/guest/cdkeys/status",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=MagicMock(read=lambda: b'{"detail":"CDK not found"}')
        )
        mock_urlopen.side_effect = err_404
        with self.assertRaises(ActivationNotFoundError):
            client.get_status()

        # 410 CdkAlreadyUsedError
        err_410 = urllib.error.HTTPError(
            url="https://shanma.store/api/guest/cdkeys/redeem",
            code=410,
            msg="Gone",
            hdrs={},
            fp=MagicMock(read=lambda: b'{"detail":"CDK already used"}')
        )
        mock_urlopen.side_effect = err_410
        with self.assertRaises(CdkAlreadyUsedError):
            client.redeem()

        # 429 RateLimitError
        err_429 = urllib.error.HTTPError(
            url="https://shanma.store/api/guest/cdkeys/sms",
            code=429,
            msg="Too Many Requests",
            hdrs={},
            fp=MagicMock(read=lambda: b'{"detail":"Rate limit exceeded"}')
        )
        mock_urlopen.side_effect = err_429
        with self.assertRaises(RateLimitError):
            client.query_sms()

    @patch.object(CodexSmsClient, "switch_phone")
    @patch.object(CodexSmsClient, "redeem")
    def test_activation_context_manager(self, mock_redeem, mock_switch):
        """Test ActivationContext manager lifecycle and switch functionality."""
        mock_redeem.return_value = OrderResult(
            activation_id="act_ctx_1",
            phone_number="+12025550199",
            service="openai",
            country="United States",
            raw={}
        )
        mock_switch.return_value = OrderResult(
            activation_id="act_ctx_2",
            phone_number="+447911123456",
            service="openai",
            country="United Kingdom",
            raw={}
        )

        client = CodexSmsClient(cdkey="CDK_TEST_123")
        with client.activation(service="chatgpt") as act:
            self.assertEqual(act.phone_number, "+12025550199")
            self.assertEqual(act.activation_id, "act_ctx_1")

            new_order = act.switch()
            self.assertEqual(act.phone_number, "+447911123456")
            self.assertEqual(act.activation_id, "act_ctx_2")

        mock_redeem.assert_called_once_with(service="chatgpt")
        mock_switch.assert_called_once()


if __name__ == "__main__":
    unittest.main()
