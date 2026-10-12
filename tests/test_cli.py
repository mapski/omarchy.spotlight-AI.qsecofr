import unittest
from unittest.mock import patch
from backend.registry import Registry
from backend.providers.base import ProviderStatus

class CliGateTests(unittest.TestCase):
    def test_detected_cli_routes_remain_independently_disabled_with_specific_gates(self):
        with patch('backend.registry.shutil.which', return_value='/synthetic/cli'), patch('subprocess.Popen', side_effect=AssertionError('Discovery must never execute a CLI')):
            registry = Registry()
            for adapter in registry.adapters.values():
                adapter.discover = lambda: ProviderStatus('local-test', False)
            statuses = [s for s in registry.discover() if s.route_id in {'codex','claude','grok','hermes','pi'}]
        self.assertEqual({s.route_id for s in statuses}, {'codex', 'claude', 'grok', 'hermes', 'pi'})
        self.assertTrue(all(not s.available and not s.models for s in statuses))
        self.assertEqual(len({s.reason for s in statuses}), 5)
        self.assertIn('credential', next(s.reason for s in statuses if s.route_id == 'pi').lower())
