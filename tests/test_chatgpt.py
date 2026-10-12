import io
import json
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from backend.chatgpt_auth import ChatGPTAuth, AUTH, API, SCOPES
from backend.providers.chatgpt import ChatGPTAdapter
from backend.protocol import Request

class Transport:
    def __init__(self): self.calls=[]; self.responses={}; self.events=[]
    def json(self,url,form=None,token=None):
        self.calls.append((url,form,token)); value=self.responses[url]
        return value() if callable(value) else value
    def stream(self,payload,token,cancel):
        self.calls.append((API+'/responses',payload,token))
        yield from self.events

class ChatGPTTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.net=Transport(); self.auth=ChatGPTAuth(Path(self.tmp.name)/'auth',self.net)
        self.key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
        jwk=json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(self.key.public_key()));jwk['kid']='fixture'
        self.net.responses[AUTH+'/.well-known/jwks.json']={'keys':[jwk]}
        self.net.responses[AUTH+'/.well-known/openid-configuration']={'issuer':AUTH,'jwks_uri':AUTH+'/.well-known/jwks.json','revocation_endpoint':AUTH+'/revoke'}
        self.tx=self.auth.transaction('http://127.0.0.1:1234/auth/callback')
    def tokens(self,**claims):
        body={'iss':AUTH,'aud':'oaiapp_fixture','sub':'fixture-sub','iat':int(time.time()),'exp':int(time.time())+300,'nonce':self.tx['nonce']};body.update(claims)
        return {'id_token':jwt.encode(body,self.key,algorithm='RS256',headers={'kid':'fixture'}),'access_token':'synthetic-access','refresh_token':'synthetic-refresh','token_type':'Bearer','expires_in':3600,'scope':' '.join(SCOPES)}
    def login(self,tokens=None,callback=None):
        self.net.responses[AUTH+'/api/accounts/oauth/token']=tokens or self.tokens()
        return self.auth.complete(self.tx,callback or {'state':self.tx['state'],'code':'synthetic-code','client_id':'oaiapp_fixture'})
    def test_pkce_host_and_callback_binding(self):
        other=self.auth.transaction('http://127.0.0.1:4321/auth/callback')
        self.assertEqual(self.tx['host_id'],other['host_id']);self.assertNotEqual(self.tx['state'],other['state'])
        self.login();form=next(c[1] for c in self.net.calls if c[1])
        self.assertEqual(form['redirect_uri'],self.tx['redirect_uri']);self.assertEqual(form['client_id'],'oaiapp_fixture')
        self.assertEqual(form['code_verifier'],self.tx['verifier'])
    def test_bad_state_never_exchanges(self):
        with self.assertRaises(ValueError):self.login(callback={'state':'bad','code':'x','client_id':'oaiapp_fixture'})
        self.assertEqual(self.net.calls,[])
    def test_replay_rejected(self):
        self.login()
        with self.assertRaises(ValueError):self.login()
    def test_bad_identity_and_scope_never_saved(self):
        for field,value in [('nonce','wrong'),('aud','wrong'),('iss','https://evil.invalid'),('exp',1)]:
            self.tx=self.auth.transaction('http://127.0.0.1:1234/auth/callback')
            with self.assertRaises(ValueError):self.login(self.tokens(**{field:value}))
            self.assertEqual(self.auth.accounts()['accounts'],[])
        self.tx=self.auth.transaction('http://127.0.0.1:1234/auth/callback');t=self.tokens();t['scope']='openid'
        with self.assertRaises(ValueError):self.login(t)
    def test_credentials_private_and_not_in_public_status(self):
        handle=self.login();public=self.auth.accounts()
        self.assertNotIn('synthetic-access',json.dumps(public));self.assertEqual(public['active'],handle)
        self.assertEqual((Path(self.tmp.name)/'auth'/'credentials.json').stat().st_mode&0o777,0o600)
    def test_reauth_wrong_subject_rejected(self):
        handle=self.login();self.tx=self.auth.transaction('http://127.0.0.1:1234/auth/callback',handle)
        with self.assertRaises(ValueError):self.login(self.tokens(sub='other'))
    def test_rotating_refresh(self):
        handle=self.login()
        with self.auth.locked() as data:
            data['accounts'][handle]['expires_at']=0;self.auth.save(data)
        t=self.tokens();t['access_token']='renewed';t['refresh_token']='rotated';self.net.responses[AUTH+'/api/accounts/oauth/token']=t
        self.assertEqual(self.auth.snapshot(handle)['access_token'],'renewed')
        self.assertEqual(self.auth.snapshot(handle)['refresh_token'],'rotated')
    def test_account_binding_and_no_tools(self):
        handle=self.login();adapter=ChatGPTAdapter(self.auth)
        self.net.responses[API+'/models']={'models':[{'slug':'fixture-model','visibility':'list'}]}
        status=adapter.discover();self.assertEqual(status.models[0].backend_id,handle)
        self.net.events=[{'type':'response.output_text.delta','delta':'hello'},{'type':'response.completed','response':{'status':'completed','model':'fixture-model','output':[]}}]
        events=list(adapter.stream(Request('r','chatgpt','fixture-model','Synthetic',backend_id=handle),threading.Event()))
        self.assertEqual(events[-1].kind,'done');payload=self.net.calls[-1][1]
        self.assertEqual(set(payload),{'model','input','store','stream','instructions'})
        self.assertFalse(payload['store']);self.assertTrue(payload['stream'])
        with self.assertRaises(ValueError):list(adapter.stream(Request('r','chatgpt','fixture-model','x',backend_id='wrong'),threading.Event()))
    def test_tool_and_incomplete_responses_fail(self):
        handle=self.login();adapter=ChatGPTAdapter(self.auth)
        self.net.responses[API+'/models']={'models':[{'slug':'m','visibility':'list'}]}
        for events in [[{'type':'response.output_item.added','item':{'type':'function_call'}}],[{'type':'response.completed','response':{'status':'completed','model':'other','output':[]}}],[{'type':'response.output_text.delta','delta':'partial'}]]:
            self.net.events=events
            with self.assertRaises(ValueError):list(adapter.stream(Request('r','chatgpt','m','x',backend_id=handle),threading.Event()))
    def test_cancel_during_exchange_cannot_sign_in(self):
        tokens=self.tokens()
        def exchange():
            self.auth.cancel_login()
            return tokens
        self.net.responses[AUTH+'/api/accounts/oauth/token']=exchange
        with self.assertRaises(ValueError):
            self.auth.complete(self.tx,{'state':self.tx['state'],'code':'x','client_id':'oaiapp_fixture'})
        self.assertEqual(self.auth.accounts()['accounts'],[])

    def test_signout_clears_tokens_retains_registration(self):
        handle=self.login();self.net.responses[AUTH+'/revoke']={}
        self.auth.store._write('login-status.json', {'stage':'complete','signed_in':True})
        self.auth.logout(handle);self.assertFalse(self.auth.accounts()['accounts'][0]['signed_in'])
        self.assertEqual(self.auth.login_status(),{})
        self.assertEqual(self.auth.transaction('http://127.0.0.1:1234/auth/callback',handle)['client_id'],'oaiapp_fixture')

    def test_signature_tampering_rejected(self):
        t=self.tokens();parts=t['id_token'].split('.');parts[2]='AAAA';t['id_token']='.'.join(parts)
        with self.assertRaises(ValueError):self.login(t)
        self.assertEqual(self.auth.accounts()['accounts'],[])

    def test_callback_server_stops_and_reports_only_public_status(self):
        import urllib.request
        from urllib.parse import urlsplit,urlencode
        events=[]
        original=self.auth.transaction
        def transaction(*args):
            self.tx=original(*args)
            self.net.responses[AUTH+'/api/accounts/oauth/token']=self.tokens()
            return self.tx
        def browser(url):
            base='http://'+urlsplit(url).netloc
            self.callback_base=base
            def callback():
                req=base+'/auth/callback?'+urlencode({'state':self.tx['state'],'code':'fixture','client_id':'oaiapp_fixture'})
                with urllib.request.urlopen(req,timeout=3) as response:
                    self.assertEqual(response.status,200)
                    self.assertIn(b'account saved successfully',response.read())
                    self.assertEqual(len(self.auth.accounts()['accounts']),1)
            self.callback_thread=threading.Thread(target=callback);self.callback_thread.start()
        with patch.object(self.auth,'transaction',side_effect=transaction):
            self.auth.login(browser,events.append)
        self.callback_thread.join(3)
        self.assertTrue(events[-1]['signed_in']);self.assertNotIn('synthetic-access',json.dumps(events))
        with self.assertRaises(OSError):urllib.request.urlopen(self.callback_base,timeout=.1)

    def test_signout_invalidates_exchange_already_in_progress(self):
        handle=self.login();self.tx=self.auth.transaction('http://127.0.0.1:1234/auth/callback',handle)
        tokens=self.tokens();self.net.responses[AUTH+'/revoke']={}
        def exchange():
            self.auth.logout(handle)
            return tokens
        self.net.responses[AUTH+'/api/accounts/oauth/token']=exchange
        with self.assertRaises(ValueError):self.auth.complete(self.tx,{'state':self.tx['state'],'code':'x'})
        self.assertFalse(self.auth.accounts()['accounts'][0]['signed_in'])

    def test_transport_rejects_other_origins_and_redirects(self):
        from backend.chatgpt_auth import Transport as RealTransport, NoRedirect
        net=RealTransport()
        with self.assertRaises(ValueError):net.json('https://evil.invalid/models',token='synthetic')
        with self.assertRaises(ValueError):net.json(AUTH+'/anything',token='synthetic')
        with self.assertRaises(ValueError):NoRedirect().redirect_request(None,None,None,None,None,None)

    def test_sse_transport_payload_and_completion(self):
        from backend.chatgpt_auth import Transport as RealTransport
        class Reply(io.BytesIO):
            def read1(self,n):return self.read(7)
        net=RealTransport()
        raw=b'data: {"type":"response.output_text.delta","delta":"ok"}\r\n\r\ndata: {"type":"response.completed"}\n\n'
        with patch.object(net.opener,'open',return_value=Reply(raw)) as opened:
            result=list(net.stream({'model':'fixture','store':False,'stream':True},'synthetic',threading.Event()))
        self.assertEqual(result[-1]['type'],'response.completed')
        req=opened.call_args.args[0];self.assertEqual(req.full_url,API+'/responses')
        self.assertEqual(req.get_header('Authorization'),'Bearer synthetic')

    def test_login_failure_reports_safe_stage(self):
        events=[]
        with patch('backend.chatgpt_auth.HTTPServer',side_effect=OSError('SECRET fixture URL')):
            self.auth.login(lambda url:None,events.append)
        self.assertEqual(events[-1]['stage'],'callback_listener')
        self.assertNotIn('SECRET',json.dumps(events))
        self.assertEqual(self.auth.login_status()['stage'],'callback_listener')
