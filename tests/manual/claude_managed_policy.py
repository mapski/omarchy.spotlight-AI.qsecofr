"""Manual reproduction of managed helper and hook execution; requires bwrap. Installed-CLI check against a synthetic HTTP fixture; never uses real credentials."""
import json, os, subprocess, tempfile, threading, signal, shutil
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
with tempfile.TemporaryDirectory(prefix='model-search-claude-mock-') as tmp:
    root=Path(tmp); project=root/'project'; project.mkdir()
    marker=root/'tool-ran'; hook_marker=root/'hook-ran'
    config=project/'.claude';config.mkdir()
    (project/'CLAUDE.md').write_text('MUST_NOT_LOAD_MODEL_SEARCH')
    (config/'settings.json').write_text(json.dumps({'hooks':{'SessionStart':[{'hooks':[{'type':'command','command':'touch '+str(hook_marker)}]}]}}))
    helper_marker=root/'helper-ran'
    managed=root/'managed';managed.mkdir()
    (managed/'managed-settings.json').write_text(json.dumps({'apiKeyHelper':'touch '+str(helper_marker)+'; printf synthetic-not-a-secret', 'hooks':{'SessionStart':[{'hooks':[{'type':'command','command':'touch '+str(hook_marker)}]}]}}))
    requests=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def do_POST(self):
            p=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            if not self.path.startswith('/v1/messages'):
                self.send_response(200);self.end_headers();self.wfile.write(b'{}');return
            requests.append(p)
            self.send_response(200);self.send_header('Content-Type','text/event-stream');self.end_headers()
            def event(name,data):
                self.wfile.write(('event: '+name+'\ndata: '+json.dumps(dict(data,type=name))+'\n\n').encode())
            event('message_start',{'message':{'id':'msg_fixture','type':'message','role':'assistant','model':'synthetic','content':[],'stop_reason':None,'stop_sequence':None,'usage':{'input_tokens':1,'output_tokens':0}}})
            if len(requests)==1:
                event('content_block_start',{'index':0,'content_block':{'type':'tool_use','id':'tool_fixture','name':'Bash','input':{}}})
                event('content_block_delta',{'index':0,'delta':{'type':'input_json_delta','partial_json':json.dumps({'command':'touch '+str(marker)})}})
                reason='tool_use'
            else:
                event('content_block_start',{'index':0,'content_block':{'type':'text','text':''}})
                event('content_block_delta',{'index':0,'delta':{'type':'text_delta','text':'Synthetic offline response'}});reason='end_turn'
            event('content_block_stop',{'index':0})
            event('message_delta',{'delta':{'stop_reason':reason,'stop_sequence':None},'usage':{'output_tokens':5}})
            event('message_stop',{})
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    env={'PATH':os.environ['PATH'],'HOME':str(root),'ANTHROPIC_BASE_URL':'http://127.0.0.1:'+str(server.server_port),'CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC':'1'}
    argv=[shutil.which('claude') or 'claude','--print','--safe-mode','--setting-sources','','--settings','{"disableAllHooks":true,"apiKeyHelper":""}','--restricted','--tools','','--strict-mcp-config','--mcp-config','{"mcpServers":{}}','--no-session-persistence','--model','synthetic','--output-format','json','--system-prompt','Answer questions only.']
    argv=['bwrap','--ro-bind','/','/','--dev','/dev','--proc','/proc','--overlay-src','/etc','--tmp-overlay','/etc','--bind',str(root),str(root),'--ro-bind',str(managed),'/etc/claude-code','--']+argv
    proc=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,cwd=project,env=env,start_new_session=True)
    timed_out=False
    try: out,err=proc.communicate('Synthetic offline safety test',timeout=25)
    except subprocess.TimeoutExpired:
        timed_out=True;os.killpg(proc.pid,signal.SIGKILL);out,err=proc.communicate()
    finally: server.shutdown();server.server_close();thread.join()
    print(json.dumps({'requests':len(requests),'tools_advertised':any(bool(p.get('tools')) for p in requests),'context_sentinel_sent':any('MUST_NOT_LOAD_MODEL_SEARCH' in json.dumps(p) for p in requests),'tool_executed':marker.exists(),'hook_executed':hook_marker.exists(),'credential_helper_executed':helper_marker.exists(),'session_files':len(list(root.rglob('*.jsonl'))),'exit_code':proc.returncode,'timeout':timed_out,'scope':'synthetic local HTTP fixture only; no inference engine or real credentials'}))
    assert helper_marker.exists() and hook_marker.exists(), 'Expected managed-policy regression was not reproduced'
    assert requests and proc.returncode == 0 and not timed_out, 'CLI fixture did not complete'
    assert not any(p.get('tools') or 'MUST_NOT_LOAD_MODEL_SEARCH' in json.dumps(p) for p in requests), 'Unexpected tools or workspace context'
    assert not marker.exists() and not list(root.rglob('*.jsonl')), 'Unexpected execution or session persistence'
