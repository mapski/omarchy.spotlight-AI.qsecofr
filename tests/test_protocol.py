import json
import unittest
from backend.protocol import parse_request


class ProtocolTests(unittest.TestCase):
    def request(self, **updates):
        data = dict(version=1, request_id='r1', route_id='codex', model_id='verified-model', prompt='Synthetic question')
        data.update(updates)
        return json.dumps(data)

    def test_request_keeps_explicit_selection(self):
        request = parse_request(self.request())
        self.assertIsNotNone(request)
        self.assertEqual((request.route_id, request.model_id, request.prompt), ('codex', 'verified-model', 'Synthetic question'))

    def test_rejects_malformed_or_ambiguous_requests(self):
        for raw in ['not json', '[]', self.request(version=2), self.request(route_id='guess'), self.request(model_id=''), self.request(prompt=''), self.request(prompt='x' * (1024 * 1024 + 1)), self.request(request_id='bad\nidentifier'), self.request(extra='unexpected'), self.request(route_id='pi')]:
            with self.subTest(raw=raw[:50]):
                with self.assertRaises(ValueError):
                    parse_request(raw)

    def test_pi_requires_explicit_backend(self):
        request = parse_request(self.request(route_id='pi', backend_id='anthropic'))
        self.assertIsNotNone(request)
        self.assertEqual(request.backend_id, 'anthropic')
