import io
import json
import unittest
from unittest.mock import patch

from jev_relay.router import route
from jev_relay.providers import openjev, ProviderUnavailable

CFG = {"local_enabled": True, "local_backend": "openjev"}
CHOICE = {"state": "An approved email send failed. Error: connection reset",
          "questions": {"failover": {"type": "choice", "instructions": "What next?",
                                     "criteria": {"retry-now": "Transient network error", "backoff": "Quota limit",
                                                  "park": "Auth failure"}}}}


def fake_service(reply):
    """Patch the opener so the adapter sees `reply` and records what it sent."""
    sent = []

    class Opener:
        def open(self, req, timeout=None):
            sent.append(json.loads(req.data))
            return io.BytesIO(json.dumps(reply(sent[-1])).encode())

    return patch("urllib.request.build_opener", return_value=Opener()), sent


class OpenJevAdapterTests(unittest.TestCase):
    def test_choice_maps_descriptions_back_to_ids_and_renormalizes(self):
        p, sent = fake_service(lambda body: {"model": "gliclass", "abstain": False, "distribution": {
            "Transient network error": .6, "Quota limit": .2, "Auth failure": .1}})  # .1 went to insufficient evidence
        with p:
            result = route(CHOICE, CFG)
        answer = result["answers"]["failover"]
        self.assertEqual(result["provider"], "local")
        self.assertEqual(answer["choice"], "retry-now")
        self.assertAlmostEqual(sum(answer["probabilities"].values()), 1.0, places=6)
        self.assertEqual(sent[0]["state"], CHOICE["state"])  # the service reads `state`; it must carry the evidence
        self.assertEqual(sent[0]["question"], "What next?")

    def test_score_and_noul(self):
        req = {"state": "s", "questions": {
            "risk": {"type": "score", "instructions": "How risky?", "criteria": ["low", "high"]},
            "ok": {"type": "noul", "instructions": "Looks fine?"}}}
        p, _ = fake_service(lambda body: {"model": "m", "abstain": True, "distribution":
                                          {"low": .25, "high": .75} if body["type"] == "score" else {"true": .3, "false": .7}})
        with p:
            result = route(req, CFG)
        self.assertAlmostEqual(result["answers"]["risk"]["score"], .75, places=6)
        self.assertAlmostEqual(result["answers"]["ok"]["noul"], .3, places=6)
        self.assertTrue(result["answers"]["ok"]["abstain"])

    def test_non_loopback_url_refused_before_any_network_call(self):
        p, sent = fake_service(lambda body: {})
        with p, self.assertRaises(ProviderUnavailable):
            openjev(CHOICE, {"openjev_url": "http://example.com:8940"})
        self.assertEqual(sent, [])

    def test_service_down_returns_review_not_exception(self):
        with patch("urllib.request.build_opener", side_effect=OSError("down")):
            result = route(CHOICE, CFG)
        self.assertEqual(result["status"], "review")
        self.assertEqual(result["attempts"][0]["reason"], "openjev_unreachable")

    def test_routine_openjev_never_touches_hosted(self):
        p, _ = fake_service(lambda body: {"model": "m", "abstain": False, "distribution": {
            "Transient network error": .5, "Quota limit": .3, "Auth failure": .2}})
        with p, patch("jev_relay.providers.hosted", side_effect=AssertionError("cloud called")):
            route(CHOICE, CFG, cloud_allowed=True, sensitive=False)


if __name__ == "__main__":
    unittest.main()
