import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from backend.providers.local import LocalAdapter
from backend.protocol import Request


class LocalTests(unittest.TestCase):
    def setUp(self):
        self.paths = []
        self.reply = {'models': [{'name': 'test-model', 'remote_host': 'cloud.example'}]}
        owner = self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass
            def do_GET(self):
                owner.paths.append(self.path)
                raw = json.dumps(owner.reply).encode()
                self.send_response(200); self.end_headers(); self.wfile.write(raw)
            def do_POST(self):
                owner.paths.append(self.path)
                self.rfile.read(int(self.headers['Content-Length']))
                self.send_response(200); self.end_headers()
                self.wfile.write(b'{"message":{"content":"Answer"},"done":true}\n')
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.endpoint = 'http://127.0.0.1:' + str(self.server.server_port)

    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join()

    def test_rejects_remote_url_even_before_discovery(self):
        with self.assertRaises(ValueError):
            LocalAdapter('ollama', 'https://example.com')

    def test_rejects_cloud_and_unknown_locality(self):
        adapter = LocalAdapter('ollama', self.endpoint)
        self.assertFalse(adapter.discover().available)
        self.assertNotIn('/api/chat', self.paths)

    def test_local_ollama_discovery_and_explicit_query(self):
        self.reply = {'models': [{'name': 'test-model', 'details': {'format': 'gguf', 'parameter_size': '1B'}}]}
        adapter = LocalAdapter('ollama', self.endpoint)
        status = adapter.discover()
        self.assertTrue(status.available)
        self.assertEqual([m.id for m in status.models], ['test-model'])
        self.assertNotIn('/api/chat', self.paths)
        result = list(adapter.stream(Request('r', 'ollama', 'test-model', 'Synthetic'), threading.Event()))
        self.assertEqual(''.join(e.text for e in result if e.kind == 'delta'), 'Answer')
        self.assertEqual(result[-1].kind, 'done')

    def test_unknown_model_never_submits(self):
        adapter = LocalAdapter('ollama', self.endpoint)
        with self.assertRaises(ValueError):
            list(adapter.stream(Request('r', 'ollama', 'missing', 'Synthetic'), threading.Event()))
        self.assertNotIn('/api/chat', self.paths)

    def test_openai_routes_only_offer_loaded_models(self):
        for route, payload in [('lmstudio', {'data': [{'id': 'loaded', 'state': 'loaded'}, {'id': 'cold', 'state': 'not-loaded'}]}), ('llamacpp', {'data': [{'id': 'loaded', 'status': {'value': 'loaded'}, 'meta': {'n_ctx_train': 2048}}, {'id': 'cold', 'status': {'value': 'unloaded'}}]})]:
            self.reply = payload
            self.assertEqual([m.id for m in LocalAdapter(route, self.endpoint).discover().models], ['loaded'])

    def test_cancel_during_discovery_never_submits_prompt(self):
        self.reply = {'models': [{'name': 'test-model', 'details': {'format': 'gguf'}}]}
        adapter = LocalAdapter('ollama', self.endpoint)
        cancel = threading.Event()
        discover = adapter.discover
        def cancelled_discovery():
            status = discover()
            cancel.set()
            return status
        adapter.discover = cancelled_discovery
        events = list(adapter.stream(Request('r', 'ollama', 'test-model', 'Synthetic'), cancel))
        self.assertNotIn('/api/chat', self.paths)
        self.assertEqual([e.kind for e in events], ['cancelled'])
