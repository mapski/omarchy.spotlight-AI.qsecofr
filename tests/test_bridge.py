import tempfile
import unittest
from pathlib import Path
from backend.main import Bridge


class BridgeTests(unittest.TestCase):
    def test_local_query_never_discovers_or_calls_ai(self):
        with tempfile.TemporaryDirectory() as tmp:
            events = []
            bridge = Bridge(Path(tmp), events.append)
            bridge.handle({'op': 'search', 'request_id': 's1', 'text': ''})
            self.assertEqual(events[-1], {'kind': 'results', 'request_id': 's1', 'results': []})
            self.assertEqual(bridge.active, {})

    def test_ai_is_rejected_before_opt_in(self):
        with tempfile.TemporaryDirectory() as tmp:
            events = []
            bridge = Bridge(Path(tmp), events.append)
            bridge.handle({'op': 'ask', 'request': {'version': 1, 'request_id': 'a1', 'route_id': 'ollama', 'model_id': 'x', 'prompt': 'Synthetic'}})
            self.assertEqual(events[-1]['kind'], 'error')
            self.assertIn('opt-in', events[-1]['text'])
            self.assertEqual(bridge.active, {})

    def test_unknown_operation_and_activation_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            events = []
            bridge = Bridge(Path(tmp), events.append)
            for message in [{'op': 'shell', 'command': 'whoami'}, {'op': 'activate', 'id': '/etc/passwd'}]:
                bridge.handle(message)
                self.assertEqual(events[-1]['kind'], 'error')

    def test_corrupt_settings_returns_error_without_crashing(self):
        with tempfile.TemporaryDirectory() as tmp:
            events = []
            bridge = Bridge(Path(tmp), events.append)
            (Path(tmp) / 'settings.json').write_text('{invalid')
            bridge.handle({'op': 'ask', 'request_id': 'broken'})
            self.assertEqual(events[-1]['kind'], 'error')
            self.assertEqual(bridge.active, {})
            bridge.handle({'op': 'cancel'})

    def test_discovery_does_not_block_search_or_start_duplicate_workers(self):
        import threading
        import time
        with tempfile.TemporaryDirectory() as tmp:
            events = []
            bridge = Bridge(Path(tmp), events.append)
            entered, release = threading.Event(), threading.Event()
            calls = []
            def discover():
                calls.append(1)
                entered.set()
                release.wait(1)
                return []
            bridge.registry.discover = discover
            start = time.monotonic()
            bridge.handle({'op': 'discover', 'request_id': 'd1'})
            elapsed = time.monotonic() - start
            try:
                self.assertLess(elapsed, .2)
                self.assertTrue(entered.wait(.2))
                bridge.handle({'op': 'discover', 'request_id': 'd2'})
                bridge.handle({'op': 'search', 'request_id': 's1', 'text': ''})
                self.assertEqual(events[-1]['kind'], 'results')
                self.assertEqual(len(calls), 1)
            finally:
                release.set()
                for thread in bridge.threads:
                    thread.join(2)
            self.assertEqual(events[-1]['kind'], 'providers')

    def test_discovery_failure_is_sanitized_and_retryable(self):
        import threading
        with tempfile.TemporaryDirectory() as tmp:
            events = []
            ready = threading.Event()
            def emit(event):
                events.append(event)
                ready.set()
            bridge = Bridge(Path(tmp), emit)
            def fail():
                raise RuntimeError('sensitive upstream diagnostic')
            bridge.registry.discover = fail
            bridge.handle({'op': 'discover', 'request_id': 'd1'})
            self.assertTrue(ready.wait(1))
            self.assertEqual(events[-1]['kind'], 'discovery_error')
            self.assertNotIn('sensitive', str(events))
            for thread in bridge.threads:
                thread.join(1)
            ready.clear()
            bridge.registry.discover = lambda: []
            bridge.handle({'op': 'discover', 'request_id': 'd2'})
            self.assertTrue(ready.wait(1))
            self.assertEqual(events[-1]['kind'], 'providers')

    def test_settings_update_preserves_opt_in_and_rejects_invalid_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            bridge = Bridge(Path(tmp), lambda e: None)
            bridge.handle({'op': 'configure', 'roots': [tmp], 'selection': {'route_id': 'ollama', 'model_id': 'demo', 'backend_id': ''}})
            settings = bridge.state.load_settings()
            self.assertEqual(settings['roots'], [tmp])
            self.assertFalse(settings['ai_enabled'])
            self.assertEqual(settings['selection']['model_id'], 'demo')
            bridge.handle({'op': 'configure', 'roots': ['relative'], 'selection': {}})
            self.assertEqual(bridge.state.load_settings(), settings)

    def test_followup_uses_saved_context_only_with_same_destination(self):
        from backend.protocol import ResponseEvent
        class Fake:
            def __init__(self): self.requests = []
            def stream(self, request, cancel):
                self.requests.append(request)
                yield ResponseEvent(request.request_id, 'delta', 'Synthetic answer')
                yield ResponseEvent(request.request_id, 'done')
        with tempfile.TemporaryDirectory() as tmp:
            events = []
            bridge = Bridge(Path(tmp), events.append)
            fake = Fake()
            bridge.registry.adapters['ollama'] = fake
            bridge.state.save_settings({'ai_enabled': True, 'roots': []})
            def ask(rid, cid='', model='demo', temporary=False):
                bridge.handle({'op': 'ask', 'request': {'version': 1, 'request_id': rid, 'route_id': 'ollama', 'model_id': model, 'prompt': 'Synthetic question', 'conversation_id': cid, 'temporary': temporary}})
                for worker in bridge.threads: worker.join(2)
            ask('a1')
            conversation = events[-1]['conversation_id']
            ask('a2', conversation)
            self.assertEqual(len(fake.requests), 2)
            self.assertEqual(len(fake.requests[-1].history), 2)
            self.assertEqual(len(bridge.state.history()[conversation]), 4)
            ask('a3', conversation, 'another')
            self.assertEqual(len(fake.requests), 2)
            ask('a4', temporary=True)
            self.assertNotIn('a4', bridge.state.history())

    def test_new_chat_request_ids_cannot_merge_after_restart(self):
        from backend.protocol import ResponseEvent
        class Fake:
            def stream(self, request, cancel):
                yield ResponseEvent(request.request_id, 'delta', 'answer')
                yield ResponseEvent(request.request_id, 'done')
        with tempfile.TemporaryDirectory() as tmp:
            ids = []
            for _ in range(2):
                events = []
                bridge = Bridge(Path(tmp), events.append)
                bridge.state.save_settings({'ai_enabled': True, 'roots': []})
                bridge.registry.adapters['ollama'] = Fake()
                bridge.handle({'op': 'ask', 'request': {'version': 1, 'request_id': 'a1', 'route_id': 'ollama', 'model_id': 'demo', 'prompt': 'New chat'}})
                for worker in bridge.threads: worker.join(2)
                ids.append(events[-1]['conversation_id'])
            self.assertNotEqual(*ids)
            self.assertEqual(len(bridge.state.history()), 2)
