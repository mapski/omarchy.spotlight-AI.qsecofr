"""Explicit native sign-in actions; never read or copy credential files.

Authentication is independent of the provider execution safety gate. No prompt
is accepted here, and signing in never registers an inference adapter.
"""
import json
import os
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path
from backend.runner import stream_process

CLAUDE_FLAGS = ['--safe-mode', '--restricted', '--setting-sources', '',
                '--settings', '{"disableAllHooks":true,"apiKeyHelper":""}']


def clean_environment():
    # Keep the native login/browser session, not API keys, helper injection,
    # alternate backends, proxies or executable runtime configuration.
    names = ('PATH', 'LANG', 'LC_ALL', 'DISPLAY', 'WAYLAND_DISPLAY',
             'XDG_RUNTIME_DIR', 'DBUS_SESSION_BUS_ADDRESS')
    env = {key: os.environ[key] for key in names if key in os.environ}
    env['HOME'] = str(Path.home())
    env['CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC'] = '1'
    return env


class AuthController:
    def __init__(self):
        self.terminals = {}

    @staticmethod
    def command(route):
        if route not in {'claude', 'codex'}:
            raise ValueError('Unsupported sign-in route')
        executable = shutil.which(route)
        if not executable:
            raise ValueError('CLI not installed')
        if Path(executable).resolve().name == 'mise':
            # Do not execute a shim: mise can evaluate directory configuration
            # and bootstrap tools before the CLI receives its safety flags.
            candidate = Path.home() / '.local/share/mise/installs' / route / 'latest/bin' / route
            if not candidate.is_file() or not os.access(candidate, os.X_OK):
                raise ValueError('Direct CLI executable unavailable')
            executable = str(candidate)
        return [executable] + (CLAUDE_FLAGS if route == 'claude' else [])

    def launch(self, route):
        argv = self.command(route)
        terminal = shutil.which('foot')
        if not terminal:
            raise ValueError('Sign-in terminal unavailable')
        previous = self.terminals.get(route)
        if previous and previous.poll() is None:
            return
        argv += ['auth', 'login'] if route == 'claude' else ['login']
        self.terminals[route] = subprocess.Popen(
            [terminal, '--title=Model Search — provider sign-in', '--hold', '--'] + argv,
            cwd='/tmp', env=clean_environment(), stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)

    def check(self, route, cancel=None):
        argv = self.command(route)
        argv += ['auth', 'status', '--json'] if route == 'claude' else ['login', 'status']
        signed_in = False
        try:
            with tempfile.TemporaryDirectory(prefix='model-search-auth-') as cwd:
                data = b''.join(stream_process(argv, b'', cancel if cancel is not None else threading.Event(),
                    timeout=10, max_bytes=16384, cwd=cwd, env=clean_environment(),
                    include_stderr=route == 'codex'))
            if route == 'claude':
                status = json.loads(data)
                signed_in = (status.get('loggedIn') is True
                             and status.get('apiProvider') == 'firstParty'
                             and status.get('authMethod') == 'claude.ai')
            else:
                # Never echo CLI diagnostics: some versions show API-key hints.
                signed_in = data.decode('utf-8', errors='replace').strip() == 'Logged in using ChatGPT'
        except (ValueError, RuntimeError, TimeoutError, OSError, AttributeError):
            pass
        return {'kind': 'auth_status', 'route_id': route, 'signed_in': signed_in,
                'text': ('Sign-in detected; provider safety verification still required'
                         if signed_in else 'Sign-in not confirmed. Use Sign in, then Check again.')}
