import json
import os
import tempfile
import unittest
from pathlib import Path
from backend.state import State


class StateTests(unittest.TestCase):
    def test_default_off_permissions_and_clear(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = State(Path(tmp) / 'state')
            self.assertFalse(state.load_settings()['ai_enabled'])
            state.save_settings({'ai_enabled': True, 'roots': []})
            self.assertTrue(state.load_settings()['ai_enabled'])
            state.append_turn('chat', {'role': 'user', 'text': 'Synthetic'})
            self.assertEqual(os.stat(state.root).st_mode & 0o777, 0o700)
            self.assertEqual(os.stat(state.root / 'history.json').st_mode & 0o777, 0o600)
            state.clear_history()
            self.assertEqual(state.history(), {})

    def test_symlink_state_and_files_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'linked').symlink_to(root, target_is_directory=True)
            with self.assertRaises(OSError):
                State(root / 'linked')
            state = State(root / 'state')
            (state.root / 'settings.json').symlink_to(root / 'victim')
            with self.assertRaises(OSError):
                state.save_settings({'ai_enabled': True})
            self.assertFalse((root / 'victim').exists())

    def test_bounded_history_and_corrupt_settings(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = State(Path(tmp) / 'state')
            for n in range(30):
                state.append_turn(str(n), {'role': 'user', 'text': 'Synthetic'})
            self.assertEqual(len(state.history()), 25)
            self.assertNotIn('0', state.history())
            (state.root / 'settings.json').write_text('{')
            with self.assertRaises(ValueError):
                state.load_settings()
            with self.assertRaises(ValueError):
                state.append_turn('x', {'role': 'user', 'text': 'x' * (1024 * 1024 + 1)})
