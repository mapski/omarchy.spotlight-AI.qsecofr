"""App-owned ChatGPT OAuth. No CLI credentials, token logging, or arbitrary endpoints."""
import base64
import contextlib
import fcntl
import hashlib
import json
import os
import secrets
import stat
import threading
import time
import uuid
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from backend.state import State
from backend.protocol import MAX_BYTES

AUTH = 'https://auth.openai.com'
API = 'https://api.openai.com/v1'
SCOPES = frozenset({'openid', 'profile', 'email', 'offline_access', 'resource.invoke', 'chatgpt.tokens.use.direct'})

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *_args, **_kwargs):
        raise ValueError('Redirect rejected')

class Transport:
    def __init__(self):
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

    def json(self, url, form=None, token=None):
        if not (url.startswith(AUTH + '/') or url == API + '/models'):
            raise ValueError('Invalid destination')
        headers = {'Accept': 'application/json'}
        body = None
        if form is not None:
            body = urllib.parse.urlencode(form).encode()
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        if token:
            if url != API + '/models': raise ValueError('Invalid bearer destination')
            headers['Authorization'] = 'Bearer ' + token
        with self.opener.open(urllib.request.Request(url, body, headers), timeout=10) as response:
            raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES: raise ValueError('Response limit')
        value = json.loads(raw) if raw else {}
        if not isinstance(value, dict): raise ValueError('Invalid response')
        return value

    def stream(self, payload, token, cancel):
        raw = json.dumps(payload).encode()
        if len(raw) > MAX_BYTES: raise ValueError('Request limit')
        if cancel.is_set(): return
        request = urllib.request.Request(API + '/responses', raw,
            {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json', 'Accept': 'text/event-stream'})
        deadline = time.monotonic() + 120
        count = 0; pending = b''; data = []
        with self.opener.open(request, timeout=5) as response:
            while not cancel.is_set():
                if time.monotonic() > deadline: raise TimeoutError('Response timeout')
                chunk = response.read1(4096)
                if not chunk: return
                count += len(chunk)
                if count > MAX_BYTES: raise ValueError('Response limit')
                pending += chunk
                while b'\n' in pending:
                    line, pending = pending.split(b'\n', 1)
                    line = line.rstrip(b'\r')
                    if not line and data:
                        event = json.loads(b'\n'.join(data)); data = []
                        if not isinstance(event, dict): raise ValueError('Invalid event')
                        yield event
                    elif line.startswith(b'data:'):
                        data.append(line[5:].lstrip(b' '))

class ChatGPTAuth:
    def __init__(self, root, transport=None):
        self.store = State(root)
        self.net = transport or Transport()
        self.mutex = threading.RLock()
        self.pending_lock = threading.Lock()
        self.commit_lock = threading.RLock()
        self.generation = 0
        self.stop = threading.Event()

    @contextlib.contextmanager
    def locked(self):
        with self.mutex:
            directory = self.store._directory()
            try:
                fd = os.open('lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600, dir_fd=directory)
            finally: os.close(directory)
            try:
                info = os.fstat(fd)
                if not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid() or info.st_nlink != 1:
                    raise ValueError('Unsafe credential lock')
                deadline = time.monotonic() + 15
                while True:
                    try: fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB); break
                    except BlockingIOError:
                        if time.monotonic() > deadline: raise TimeoutError('Account busy')
                        time.sleep(.05)
                data = self.store._read('credentials.json', {'accounts': {}, 'active': '', 'host_id': 'urn:uuid:' + str(uuid.uuid4())})
                if not isinstance(data.get('accounts'), dict): raise ValueError('Invalid accounts')
                yield data
            finally: os.close(fd)

    def save(self, data): self.store._write('credentials.json', data)

    def login_generation(self):
        with self.commit_lock: return self.generation

    def cancel_login(self):
        with self.commit_lock:
            self.generation += 1
            self.stop.set()

    def login_status(self):
        data = self.store._read('login-status.json', {})
        # Only records constructed here are returned; never arbitrary stored text.
        stage = data.get('stage')
        if stage not in {'callback_listener','registration_storage','browser_launch','browser_callback',
                         'token_exchange','identity_validation','permissions','credential_storage','complete'}:
            return {}
        ok = data.get('signed_in') is True and stage == 'complete'
        text = 'ChatGPT account saved successfully.' if ok else 'ChatGPT sign-in failed at ' + stage.replace('_',' ') + '. Retry Continue with ChatGPT.'
        return {'kind':'auth_status','route_id':'chatgpt','signed_in':ok,'stage':stage,'text':text}

    def accounts(self):
        with self.locked() as data:
            return {'active': data['active'], 'accounts': [
                {'id': key, 'label': str(value.get('email') or 'ChatGPT account')[:160] + ' · ' + key[:8],
                 'signed_in': bool(value.get('access_token'))}
                for key, value in data['accounts'].items()]}

    def select(self, handle):
        with self.locked() as data:
            if handle not in data['accounts']: raise ValueError('Unknown account')
            data['active'] = handle; data['generation'] = data.get('generation',0)+1; self.save(data)
            self.store._write('login-status.json', {})

    def transaction(self, redirect, handle=''):
        with self.locked() as data:
            account = data['accounts'].get(handle) if handle else None
            if handle and account is None: raise ValueError('Unknown account')
            self.save(data)  # Persist host ID before the first browser visit.
            return {'state': secrets.token_urlsafe(32), 'nonce': secrets.token_urlsafe(32),
                'verifier': secrets.token_urlsafe(48), 'redirect_uri': redirect,
                'host_id': data['host_id'], 'client_id': account['client_id'] if account else 'dynamic_agent_client',
                'subject': account['subject'] if account else '', 'handle': handle,
                'expires': time.monotonic() + 600, 'used': False, 'generation': self.generation, 'credential_generation': data.get('generation',0)}

    def authorization_url(self, tx):
        query = {'client_id': tx['client_id'], 'ext_agent_host_id': tx['host_id'],
            'response_type': 'code', 'redirect_uri': tx['redirect_uri'], 'scope': ' '.join(sorted(SCOPES)),
            'resource': API, 'state': tx['state'], 'nonce': tx['nonce'], 'code_challenge_method': 'S256',
            'code_challenge': base64.urlsafe_b64encode(hashlib.sha256(tx['verifier'].encode()).digest()).rstrip(b'=').decode()}
        if tx['client_id'] == 'dynamic_agent_client': query['agent_name_hint'] = 'Omarchy Model Search'
        # Hints deliberately omitted: avoid retained ID tokens in browser-launch arguments.
        return AUTH + '/api/accounts/authorize?' + urllib.parse.urlencode(query)

    def metadata(self):
        data = self.net.json(AUTH + '/.well-known/openid-configuration')
        if data.get('issuer') != AUTH or data.get('jwks_uri') != AUTH + '/.well-known/jwks.json':
            raise ValueError('Invalid identity metadata')
        return data

    def identity(self, token, client, nonce=None):
        import jwt
        try:
            self.metadata()
            header = jwt.get_unverified_header(token)
            if header.get('alg') not in {'RS256', 'ES256'} or not isinstance(header.get('kid'), str):
                raise ValueError('Invalid signature algorithm')
            keys = self.net.json(AUTH + '/.well-known/jwks.json').get('keys', [])
            matches = [key for key in keys if key.get('kid') == header['kid']]
            if len(matches) != 1: raise ValueError('Unknown signing key')
            key = jwt.PyJWK.from_dict(matches[0], algorithm=header['alg'])
            claims = jwt.decode(token, key.key, algorithms=[header['alg']], issuer=AUTH, audience=client,
                leeway=5, options={'require': ['iss', 'aud', 'sub', 'exp', 'iat']})
            if not isinstance(claims['sub'], str) or not claims['sub']: raise ValueError('Invalid identity')
            if nonce is not None and claims.get('nonce') != nonce: raise ValueError('Invalid nonce')
            if isinstance(claims['aud'], list) and len(claims['aud']) > 1 and claims.get('azp') != client:
                raise ValueError('Invalid authorized party')
            return claims
        except (jwt.PyJWTError, KeyError, TypeError) as exc:
            raise ValueError('Identity validation failed') from None

    def record(self, tokens, client, subject, email='', old=None):
        scopes = set(tokens.get('scope', '').split())
        if not SCOPES.issubset(scopes) or tokens.get('token_type', '').lower() != 'bearer':
            raise ValueError('ChatGPT plan permission missing')
        if any(not isinstance(tokens.get(k), str) or not tokens[k] for k in ['access_token', 'refresh_token']):
            raise ValueError('Credentials incomplete')
        lifetime = tokens.get('expires_in')
        if type(lifetime) is not int or not 0 < lifetime <= 86400: raise ValueError('Invalid expiry')
        return {'client_id': client, 'subject': subject, 'email': email, 'access_token': tokens['access_token'],
                'refresh_token': tokens['refresh_token'], 'id_token': tokens.get('id_token', (old or {}).get('id_token', '')),
                'scopes': sorted(scopes), 'expires_at': time.time() + lifetime}

    def complete(self, tx, callback, progress=lambda stage: None):
        if tx['used'] or time.monotonic() > tx['expires'] or not secrets.compare_digest(callback.get('state',''), tx['state']):
            raise ValueError('Invalid or expired callback')
        tx['used'] = True
        if callback.get('error'): raise ValueError('Authorization declined')
        client = callback.get('client_id', tx['client_id'])
        if not isinstance(client, str) or not client.startswith('oaiapp_') or len(client) > 256:
            raise ValueError('Registration incomplete')
        if tx['client_id'] != 'dynamic_agent_client' and client != tx['client_id']: raise ValueError('Registration changed')
        code = callback.get('code')
        if not isinstance(code, str) or not code or len(code) > 8192: raise ValueError('Missing code')
        progress('token_exchange')
        tokens = self.net.json(AUTH + '/api/accounts/oauth/token', form={'grant_type':'authorization_code',
            'client_id':client, 'code':code, 'code_verifier':tx['verifier'], 'redirect_uri':tx['redirect_uri'], 'resource':API})
        progress('identity_validation')
        claims = self.identity(tokens.get('id_token',''), client, tx['nonce'])
        if tx['subject'] and claims['sub'] != tx['subject']: raise ValueError('Account changed')
        progress('permissions')
        record = self.record(tokens, client, claims['sub'], claims.get('email',''))
        handle = hashlib.sha256((client+'\0'+claims['sub']).encode()).hexdigest()
        progress('credential_storage')
        with self.locked() as data:
            with self.commit_lock:
                if self.stop.is_set() or tx['generation'] != self.generation or tx['credential_generation'] != data.get('generation',0):
                    raise ValueError('Login cancelled or superseded')
                data['accounts'][handle] = record; data['active'] = handle
                data['generation'] = data.get('generation',0)+1
                self.save(data)
        return handle

    def snapshot(self, handle=None):
        with self.locked() as data:
            handle = handle or data['active']
            if not handle or handle != data['active']: raise ValueError('Selected account changed')
            account = data['accounts'].get(handle)
            if not account or not account.get('access_token'): raise ValueError('Sign in required')
            if account['expires_at'] <= time.time() + 60:
                tokens = self.net.json(AUTH + '/api/accounts/oauth/token', form={'grant_type':'refresh_token',
                    'client_id':account['client_id'], 'refresh_token':account['refresh_token'], 'resource':API})
                if tokens.get('id_token'):
                    claims = self.identity(tokens['id_token'], account['client_id'])
                    if claims['sub'] != account['subject']: raise ValueError('Refresh identity changed')
                renewed = self.record(tokens, account['client_id'], account['subject'], account.get('email',''), account)
                data['accounts'][handle] = account = renewed; self.save(data)
            return dict(account, handle=handle)

    def logout(self, handle):
        self.cancel_login()
        confirmed = False
        with self.locked() as data:
            account = data['accounts'].get(handle)
            if not account: raise ValueError('Unknown account')
            try:
                endpoint = self.metadata().get('revocation_endpoint','')
                if urllib.parse.urlsplit(endpoint).netloc != 'auth.openai.com' or not endpoint.startswith(AUTH+'/'):
                    raise ValueError('Invalid revocation destination')
                if account.get('refresh_token'):
                    self.net.json(endpoint, form={'token':account['refresh_token'],'token_type_hint':'refresh_token','client_id':account['client_id']})
                confirmed = True
            except Exception: pass
            self.store._write('login-status.json', {})
            for name in ['access_token','refresh_token','id_token','expires_at','scopes']: account.pop(name,None)
            data['generation'] = data.get('generation',0)+1
            self.save(data)
        return confirmed

    def login(self, open_browser, emit, handle='', expected_generation=None):
        if not self.pending_lock.acquire(blocking=False): raise ValueError('Login already running')
        owner = self; completed = threading.Event(); result = {}; started = False
        stage = 'callback_listener'
        def progress(value):
            nonlocal stage
            stage = value
        try:
            with self.commit_lock:
                if expected_generation is not None and expected_generation != self.generation:
                    raise ValueError('Sign-in cancelled')
                expected_generation = self.generation
                self.stop.clear()
            class Handler(BaseHTTPRequestHandler):
                def log_message(self,*args): pass
                def setup(self):
                    super().setup(); self.connection.settimeout(2)
                def do_GET(self):
                    nonlocal started
                    if len(self.path)>16384 or self.headers.get('Host') != '127.0.0.1:'+str(self.server.server_port):
                        self.send_error(400); return
                    path=urllib.parse.urlsplit(self.path)
                    if path.path == '/start' and secrets.compare_digest(path.query,ticket) and not started:
                        started=True
                        self.send_response(302);self.send_header('Location',owner.authorization_url(tx));self.send_header('Cache-Control','no-store');self.end_headers();return
                    if path.path != '/auth/callback' or completed.is_set(): self.send_error(404); return
                    try:
                        values=urllib.parse.parse_qs(path.query,keep_blank_values=True,max_num_fields=12)
                        if any(len(v)!=1 for v in values.values()): raise ValueError('Duplicate callback')
                        callback={k:v[0] for k,v in values.items()}
                        if not secrets.compare_digest(callback.get('state',''),tx['state']): raise ValueError('Invalid state')
                        result.update(callback);completed.set()
                        try:
                            owner.complete(tx,result,progress)
                            result['saved'] = True
                            body=b'ChatGPT account saved successfully. Return to Omarchy Model Search.'
                        except Exception:
                            result['saved'] = False
                            body=b'ChatGPT sign-in was not saved. Reopen Model Search for the failing step and retry.'
                        self.send_response(200);self.send_header('Content-Type','text/plain');self.send_header('Cache-Control','no-store');self.send_header('Referrer-Policy','no-referrer');self.end_headers();self.wfile.write(body)
                    except (ValueError,TypeError): self.send_error(400)
            with HTTPServer(('127.0.0.1',0),Handler) as server:
                server.timeout=.25
                progress('registration_storage')
                tx=self.transaction('http://127.0.0.1:'+str(server.server_port)+'/auth/callback',handle)
                ticket=secrets.token_urlsafe(32)
                with self.commit_lock:
                    if self.stop.is_set() or expected_generation != self.generation:
                        raise ValueError('Sign-in cancelled')
                    progress('browser_launch')
                    open_browser('http://127.0.0.1:'+str(server.server_port)+'/start?'+ticket)
                emit({'kind':'auth_opened','text':'Complete Continue with ChatGPT in your browser. Reopen the palette to check status.'})
                progress('browser_callback')
                while not completed.is_set() and not self.stop.is_set() and time.monotonic()<tx['expires']:
                    server.handle_request()
                if self.stop.is_set() or not completed.is_set(): raise ValueError('Sign-in cancelled or expired')
                if not result.get('saved'): raise ValueError('Sign-in not saved')
            progress('complete')
            self.store._write('login-status.json', {'stage':stage,'signed_in':True})
            emit(self.login_status())
        except Exception:
            event={'kind':'auth_status','route_id':'chatgpt','signed_in':False,'stage':stage,
                   'text':'ChatGPT sign-in failed at '+stage.replace('_',' ')+'. Retry Continue with ChatGPT.'}
            try: self.store._write('login-status.json', {'stage':stage,'signed_in':False})
            except Exception: pass
            emit(event)
        finally: self.pending_lock.release()
