import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from backend.providers.claude import ClaudeAdapter, policy_clear, invocation
from backend.protocol import Request

class ClaudeTests(unittest.TestCase):
    def test_user_requested_execution_gate_blocks_before_any_process(self):
        a=ClaudeAdapter()
        with patch('backend.providers.claude.stream_process',side_effect=AssertionError('must not launch')):
            with self.assertRaisesRegex(ValueError,'remains blocked'):
                list(a.stream(Request('r','claude','claude-sonnet-5-5','Synthetic'),threading.Event()))

    def test_policy_files_and_symlinks_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            home=Path(tmp); (home/'.claude').mkdir(); system=home/'system'
            self.assertTrue(policy_clear(home, system))
            (home/'.claude/remote-settings.json').write_text('{}')
            self.assertFalse(policy_clear(home, system))
            (home/'.claude/remote-settings.json').unlink()
            system.symlink_to(home/'missing')
            self.assertFalse(policy_clear(home, system))

    def test_only_personal_native_auth_and_tested_version_pass(self):
        a=ClaudeAdapter()
        with patch('backend.providers.claude.EXECUTION_APPROVED', True), patch('backend.providers.claude.policy_clear', return_value=True), patch.object(a,'_inspect', return_value=('2.1.296 (Claude Code)', {'loggedIn':True,'authMethod':'claude.ai','apiProvider':'firstParty','subscriptionType':'pro'})):
            self.assertTrue(a.refresh(threading.Event()).available)
        for plan in ('team','enterprise',None):
            with patch('backend.providers.claude.EXECUTION_APPROVED', True), patch('backend.providers.claude.policy_clear', return_value=True), patch.object(a,'_inspect', return_value=('2.1.296 (Claude Code)', {'loggedIn':True,'authMethod':'claude.ai','apiProvider':'firstParty','subscriptionType':plan})):
                self.assertFalse(a.refresh(threading.Event()).available)
        with patch('backend.providers.claude.EXECUTION_APPROVED', True), patch('backend.providers.claude.policy_clear', return_value=True), patch.object(a,'_inspect', return_value=('2.1.297 (Claude Code)', {})):
            self.assertFalse(a.refresh(threading.Event()).available)

    def test_unknown_version_does_not_launch_auth_status(self):
        a=ClaudeAdapter()
        with patch('backend.providers.claude.AuthController.command',return_value=['/synthetic/claude']), patch('backend.providers.claude.stream_process',return_value=iter([b'2.1.297 (Claude Code)'])) as run:
            version, auth=a._inspect(threading.Event())
        self.assertEqual(auth,{})
        self.assertEqual(run.call_count,1)

    def test_policy_rejection_launches_nothing(self):
        a=ClaudeAdapter()
        with patch('backend.providers.claude.policy_clear', return_value=False), patch.object(a,'_inspect', side_effect=AssertionError('must not launch')):
            self.assertFalse(a.refresh(threading.Event()).available)

    def test_profile_disables_tools_customizations_and_fallback(self):
        argv=invocation('/usr/bin/claude','claude-sonnet-5-5')
        self.assertNotIn('--bare',argv)
        self.assertEqual(argv[argv.index('--tools')+1],'')
        settings=json.loads(argv[argv.index('--settings')+1])
        self.assertFalse(settings['switchModelsOnFlag'])
        self.assertEqual(settings['fallbackModel'],[])
        self.assertIn('--disable-slash-commands',argv)

    def test_stream_checks_readiness_again_and_rejects_unselected_model(self):
        a=ClaudeAdapter(); req=Request('r','claude','claude-sonnet-5-5','Synthetic')
        with patch.object(a,'refresh',return_value=a.status), patch('backend.providers.claude.stream_process',side_effect=AssertionError('must not launch')):
            with self.assertRaises(ValueError): list(a.stream(req,threading.Event()))

    def test_stream_parses_text_and_requires_success_result(self):
        a=ClaudeAdapter()
        from backend.providers.base import ProviderStatus,Model
        ready=ProviderStatus('claude',True,models=(Model('claude-sonnet-5-5'),))
        events=[{'type':'stream_event','event':{'type':'content_block_delta','delta':{'type':'text_delta','text':'Hello'}}},{'type':'result','subtype':'success','is_error':False,'result':'Hello','modelUsage':{'claude-sonnet-5-5':{}}}]
        raw=b''.join(json.dumps(e).encode()+b'\n' for e in events)
        with patch('backend.providers.claude.EXECUTION_APPROVED',True), patch.object(a,'refresh',return_value=ready), patch('backend.providers.claude.policy_clear',return_value=True), patch('backend.providers.claude.AuthController.command',return_value=['/usr/bin/claude']), patch('backend.providers.claude.stream_process',return_value=iter([raw[:19],raw[19:]])):
            out=list(a.stream(Request('r','claude','claude-sonnet-5-5','Synthetic'),threading.Event()))
        self.assertEqual([e.kind for e in out],['delta','done'])
        self.assertEqual(out[0].text,'Hello')
