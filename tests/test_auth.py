import os
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from backend.auth import AuthController, clean_environment

class AuthTests(unittest.TestCase):
    def test_environment_drops_secrets_helpers_and_endpoint_overrides(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY":"private", "ANTHROPIC_BASE_URL":"http://wrong", "CODEX_HOME":"/wrong", "BASH_ENV":"/helper", "NODE_OPTIONS":"--require helper"}):
            env = clean_environment()
        self.assertFalse(any(k in env for k in ("ANTHROPIC_API_KEY", "ANTHROPIC_BASE_URL", "CODEX_HOME", "BASH_ENV", "NODE_OPTIONS")))
        self.assertIn("HOME", env)

    @patch("backend.auth.shutil.which", return_value="/usr/bin/claude")
    def test_only_fixed_login_commands_and_no_prompt_interpolation(self, _):
        auth = AuthController()
        with patch("backend.auth.subprocess.Popen") as launch:
            auth.launch("claude")
            args = launch.call_args.args[0]
            self.assertEqual(args[-2:], ["auth", "login"])
            self.assertNotIn("-c", args)
            self.assertFalse(launch.call_args.kwargs.get("shell", False))
            with self.assertRaises(ValueError): auth.launch("claude; touch marker")
            self.assertEqual(launch.call_count, 1)

    def test_mise_shim_is_resolved_without_running_mise(self):
        with patch('backend.auth.shutil.which', return_value='/home/test/.local/share/mise/shims/codex'), patch('backend.auth.Path.resolve', return_value=Path('/usr/bin/mise')), patch('backend.auth.Path.is_file', return_value=True), patch('backend.auth.os.access', return_value=True):
            command = AuthController.command('codex')
        self.assertIn('/installs/codex/latest/bin/codex', command[0])

    def test_status_is_sanitized_and_does_not_enable_execution(self):
        auth = AuthController()
        payload = b'{"loggedIn":true,"authMethod":"claude.ai","apiProvider":"firstParty","email":"private"}'
        with patch("backend.auth.shutil.which", return_value="/usr/bin/claude"), patch("backend.auth.stream_process", return_value=iter([payload])):
            result = auth.check("claude")
        self.assertEqual(result["signed_in"], True)
        self.assertNotIn("private", str(result))
        self.assertNotIn("available", result)

    def test_malformed_or_failed_status_fails_closed(self):
        auth = AuthController()
        with patch("backend.auth.shutil.which", return_value="/usr/bin/claude"), patch("backend.auth.stream_process", return_value=iter([b'{"loggedIn":"yes"}'])):
            self.assertFalse(auth.check("claude")["signed_in"])
        with patch("backend.auth.shutil.which", return_value="/usr/bin/codex"), patch("backend.auth.stream_process", side_effect=RuntimeError("secret")):
            result = auth.check("codex")
        self.assertFalse(result["signed_in"])
        self.assertNotIn("secret", str(result))
