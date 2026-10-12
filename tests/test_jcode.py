import hashlib
import http.client
from urllib.parse import urlsplit
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from backend.protocol import Request
from backend.providers.base import Model, ProviderStatus
from backend.providers.jcode import JcodeAdapter, parse_events, fixed_destination

class JcodeTests(unittest.TestCase):
    def test_stream_checks_destination_and_requires_successful_completion(self):
        request = Request('r', 'jcode', 'fixture', 'question', backend_id='lmstudio')
        def events(items):
            return [(json.dumps(item)+'\n').encode() for item in items]
        start = {'type':'start','provider':'spotlight-local','model':'fixture'}
        done = {'type':'done','provider':'spotlight-local','model':'fixture','text':'Answer'}
        result=list(parse_events(events([start,{'type':'text_delta','text':'Answer'},done]),request))
        self.assertEqual(''.join(e.text for e in result),'Answer')
        for invalid in [[dict(start,model='wrong')], [start,{'type':'tool_exec'}], [start,{'type':'error','message':'secret'}], [start,{'type':'text_delta','text':'partial'}]]:
            with self.assertRaises(ValueError): list(parse_events(events(invalid),request))

    def test_wrong_backend_or_unloaded_model_never_starts_process(self):
        a=JcodeAdapter()
        with patch.object(a,'discover',return_value=ProviderStatus('jcode',True,models=(Model('loaded','lmstudio','local'),))), patch('backend.providers.jcode.stream_process',side_effect=AssertionError('must not execute')):
            for model,backend in [('missing','lmstudio'),('loaded','claude'),('loaded','')]:
                with self.assertRaises(ValueError): list(a.stream(Request('r','jcode',model,'question',backend_id=backend),threading.Event()))

    def test_unverified_binary_is_never_available(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'jcode';p.write_bytes(b'not the reviewed binary');p.chmod(0o700)
            a=JcodeAdapter(p)
            self.assertFalse(a.discover().available)

    def test_cancel_before_discovery_never_launches(self):
        a=JcodeAdapter();cancel=threading.Event();cancel.set()
        with patch.object(a,'discover',side_effect=AssertionError('cancelled')):
            self.assertEqual(list(a.stream(Request('r','jcode','fixture','q',backend_id='lmstudio'),cancel)),[])

    def test_cancel_during_relay_upload_never_forwards(self):
        a=JcodeAdapter();cancel=threading.Event()
        body=json.dumps({'model':'fixture','stream':True,'messages':[]}).encode()
        with patch.object(a.local.opener,'open',side_effect=AssertionError('cancelled upload must not forward')):
            with fixed_destination(a.local,'fixture',cancel) as url:
                parts=urlsplit(url);client=http.client.HTTPConnection(parts.hostname,parts.port,timeout=2)
                client.putrequest('POST',parts.path+'/chat/completions')
                client.putheader('Content-Length',str(len(body)));client.endheaders()
                cancel.set();client.send(body)
                self.assertEqual(client.getresponse().status,400)
                client.close()
