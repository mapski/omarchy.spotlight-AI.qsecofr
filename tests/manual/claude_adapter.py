"""Run the production parser/profile against loopback fixtures, never real auth.

Usage: PYTHONPATH=. python tests/manual/claude_adapter.py [text|tool|error]
"""
import json, os, shutil, sys, tempfile, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from backend.providers.claude import ClaudeAdapter, MODELS
from backend.providers.base import ProviderStatus, Model
from backend.protocol import Request

mode = sys.argv[1] if len(sys.argv) > 1 else 'text'
assert mode in {'text', 'tool', 'error'}
with tempfile.TemporaryDirectory(prefix='model-search-claude-adapter-') as tmp:
    root=Path(tmp); (root/'.claude').mkdir()
    marker=root/'hook-ran'; tool=root/'tool-ran'; helper=root/'helper-ran'
    (root/'.claude/settings.json').write_text(json.dumps({'apiKeyHelper':'touch '+str(helper), 'hooks':{'SessionStart':[{'hooks':[{'type':'command','command':'touch '+str(marker)}]}]}, 'fallbackModel':['claude-opus-5-5']}))
    (root/'CLAUDE.md').write_text('MUST_NOT_LOAD_CONTEXT')
    requests=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def do_POST(self):
            body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            if not self.path.startswith('/v1/messages'):
                self.send_response(200);self.end_headers();self.wfile.write(b'{}');return
            requests.append(body)
            if mode=='error':
                self.send_response(400);self.send_header('Content-Type','application/json');self.end_headers()
                self.wfile.write(b'{"type":"error","error":{"type":"invalid_request_error","message":"Synthetic failure"}}');return
            self.send_response(200);self.send_header('Content-Type','text/event-stream');self.end_headers()
            def event(name,data):
                self.wfile.write(('event: '+name+'\ndata: '+json.dumps(dict(data,type=name))+'\n\n').encode())
            event('message_start',{'message':{'id':'msg_fixture','type':'message','role':'assistant','model':MODELS[0],'content':[],'stop_reason':None,'stop_sequence':None,'usage':{'input_tokens':1,'output_tokens':0}}})
            if mode=='tool':
                event('content_block_start',{'index':0,'content_block':{'type':'tool_use','id':'tool_fixture','name':'Bash','input':{}}})
                event('content_block_delta',{'index':0,'delta':{'type':'input_json_delta','partial_json':json.dumps({'command':'touch '+str(tool)})}})
            else:
                event('content_block_start',{'index':0,'content_block':{'type':'text','text':''}})
                event('content_block_delta',{'index':0,'delta':{'type':'text_delta','text':'Synthetic fixture answer'}})
            event('content_block_stop',{'index':0})
            event('message_delta',{'delta':{'stop_reason':'tool_use' if mode=='tool' else 'end_turn','stop_sequence':None},'usage':{'output_tokens':5}})
            event('message_stop',{})
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    env={'PATH':'/usr/bin:/bin','HOME':str(root),'ANTHROPIC_API_KEY':'synthetic-not-a-secret','ANTHROPIC_BASE_URL':'http://127.0.0.1:'+str(server.server_port),'CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC':'1'}
    adapter=ClaudeAdapter(); ready=ProviderStatus('claude',True,models=(Model(MODELS[0]),))
    output=[]; failed=False
    try:
        with patch('backend.providers.claude.EXECUTION_APPROVED',True), patch.object(adapter,'refresh',return_value=ready), patch('backend.providers.claude.policy_clear',return_value=True), patch('backend.providers.claude.clean_environment',return_value=env), patch('backend.providers.claude.AuthController.command',return_value=[shutil.which('claude')]):
            try: output=list(adapter.stream(Request('fixture','claude',MODELS[0],'SYNTHETIC_PRIVATE_PROMPT_8473'),threading.Event()))
            except (RuntimeError,ValueError): failed=True
    finally: server.shutdown();server.server_close();thread.join()
    persisted=[]
    for file in root.rglob('*'):
        if file.is_file() and file.stat().st_size < 4*1024*1024:
            if b'SYNTHETIC_PRIVATE_PROMPT_8473' in file.read_bytes():persisted.append(str(file.relative_to(root)))
    summary={'mode':mode,'requests':len(requests),'models':sorted({r.get('model','') for r in requests}), 'tools':any(r.get('tools') for r in requests),'context':any('MUST_NOT_LOAD_CONTEXT' in json.dumps(r) for r in requests),'hook':marker.exists(),'helper':helper.exists(),'tool':tool.exists(),'persisted_prompt_files':persisted,'session_files':len(list(root.rglob('*.jsonl'))),'completed':any(e.kind=='done' for e in output),'failed':failed}
    print(json.dumps(summary))
    assert requests and not any((summary['tools'],summary['context'],summary['hook'],summary['helper'],summary['tool'],persisted,summary['session_files']))
    assert summary['models']==[MODELS[0]]
    assert summary['completed']==(mode=='text') and failed==(mode!='text')
