import unittest
from unittest.mock import patch

from domain_onboarding import onboard_sending_domain


class DomainOnboardingTest(unittest.TestCase):
    @patch("domain_onboarding.InfraiClient")
    def test_verified_domain_sends_a_test_message(self, client_type):
        client = client_type.return_value
        client.request.side_effect = [
            {"ok": True, "data": {"verification": {"status": "verified"}}},
            {"ok": True, "data": {"message_id": "msg_demo"}},
        ]

        result = onboard_sending_domain("track.example", "ops@example.net")

        self.assertEqual(result["verification_status"], "verified")
        self.assertEqual(result["message_id"], "msg_demo")
        self.assertEqual(client.request.call_count, 2)


if __name__ == "__main__":
    unittest.main()
