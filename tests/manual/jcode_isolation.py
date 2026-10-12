"""Offline real-binary acceptance: no credentials or model engine involved."""
import argparse
import json
import sys
import tempfile
import threading
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.providers.jcode import JcodeAdapter
from backend.protocol import Request

parser=argparse.ArgumentParser();parser.add_argument('binary');args=parser.parse_args()
requests=[]; malicious=False; redirect=False; escaped=[]
with tempfile.TemporaryDirectory(prefix='jcode-marker-') as temp:
    marker=Path(temp)/'executed'
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*_): pass
        def do_GET(self):
            self.send_response(200);self.end_headers()
            self.wfile.write(json.dumps({'data':[{'id':'qa-fixture','state':'loaded'}]}).encode())
        def do_POST(self):
            body=json.loads(self.rfile.read(int(self.headers['Content-Length'])));requests.append(body)
            if self.path == '/escaped':
                escaped.append(body);self.send_response(400);self.end_headers();return
            if redirect:
                self.send_response(307);self.send_header('Location','http://127.0.0.1:'+str(self.server.server_port)+'/escaped');self.end_headers();return
            self.send_response(200);self.send_header('Content-Type','text/event-stream');self.end_headers()
            if malicious:
                delta={'role':'assistant','tool_calls':[{'index':0,'id':'probe','type':'function','function':{'name':'bash','arguments':json.dumps({'command':'touch '+str(marker)})}}]}
                finish='tool_calls'
            else:
                delta={'role':'assistant','content':'fixture answer'};finish='stop'
            for d,f in [(delta,None),({},finish)]:
                data={'id':'test','object':'chat.completion.chunk','model':'qa-fixture','choices':[{'index':0,'delta':d,'finish_reason':f}]}
                self.wfile.write(('data: '+json.dumps(data)+'\n\n').encode())
            self.wfile.write(b'data: [DONE]\n\n')
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        adapter=JcodeAdapter(args.binary,'http://127.0.0.1:'+str(server.server_port))
        request=Request('fixture','jcode','qa-fixture','Synthetic question',backend_id='lmstudio')
        events=list(adapter.stream(request,threading.Event()))
        assert events[-1].kind=='done'
        assert ''.join(e.text for e in events)=='fixture answer'
        assert len(requests)==1 and not requests[0].get('tools')
        malicious=True
        try:
            list(adapter.stream(request,threading.Event()))
            raise AssertionError('Unsolicited tool response accepted')
        except ValueError:
            pass
        assert len(requests)==2 and not requests[-1].get('tools')
        assert not marker.exists(), 'Tool executed'
        malicious=False;redirect=True
        try:
            list(adapter.stream(request,threading.Event()))
        except (ValueError,RuntimeError):
            pass
        assert not escaped, 'Prompt followed an upstream redirect'
        print('PASS: real jcode answer, no tools, unsolicited tool rejection, no inference redirects')
    finally:
        server.shutdown();server.server_close();thread.join()
