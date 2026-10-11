"""Manual installed-CLI check against a synthetic HTTP fixture; never uses real credentials."""
import json, os, subprocess, tempfile, threading, signal, shutil
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
with tempfile.TemporaryDirectory(prefix='model-search-pi-mock-') as tmp:
    root=Path(tmp); agent=root/'agent'; agent.mkdir(); project=root/'project'; project.mkdir()
    marker=root/'tool-ran'; extension_marker=root/'extension-ran'
    ext=project/'.pi/extensions'; ext.mkdir(parents=True)
    (ext/'probe.ts').write_text('import { writeFileSync } from "node:fs"; writeFileSync('+json.dumps(str(extension_marker))+',"bad"); export default function() {}')
    (project/'AGENTS.md').write_text('MUST_NOT_LOAD_MODEL_SEARCH')
    requests=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def do_POST(self):
            payload=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            requests.append(payload)
            self.send_response(200); self.send_header('Content-Type','text/event-stream'); self.end_headers()
            if len(requests)==1:
                delta={'role':'assistant','tool_calls':[{'index':0,'id':'synthetic_call','type':'function','function':{'name':'bash','arguments':json.dumps({'command':'touch '+str(marker)})}}]}
                finish='tool_calls'
            else:
                delta={'role':'assistant','content':'Synthetic offline response'}; finish='stop'
            for choice in [{'delta':delta,'finish_reason':None},{'delta':{},'finish_reason':finish}]:
                choice['index']=0
                self.wfile.write(('data: '+json.dumps({'id':'fixture','object':'chat.completion.chunk','created':0,'model':'demo','choices':[choice]})+'\n\n').encode())
            self.wfile.write(b'data: [DONE]\n\n')
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
    (agent/'models.json').write_text(json.dumps({'providers':{'fixture':{'baseUrl':'http://127.0.0.1:'+str(server.server_port)+'/v1','api':'openai-completions','apiKey':'synthetic-not-a-secret','models':[{'id':'demo','contextWindow':8192,'maxTokens':256}]}}}))
    env={'PATH':os.environ['PATH'],'HOME':str(root),'PI_CODING_AGENT_DIR':str(agent),'PI_OFFLINE':'1','PI_TELEMETRY':'0'}
    argv=[shutil.which('pi') or 'pi','--print','--mode','json','--provider','fixture','--model','demo','--system-prompt','Answer questions only.','--no-session','--no-tools','--no-extensions','--no-mcp','--no-skills','--no-prompt-templates','--no-context-files','--no-themes','--no-approve','--offline']
    proc=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,cwd=project,env=env,start_new_session=True)
    timed_out=False
    try:
        out,err=proc.communicate('Synthetic offline safety test',timeout=20)
    except subprocess.TimeoutExpired:
        timed_out=True
        os.killpg(proc.pid,signal.SIGKILL);out,err=proc.communicate()
    finally:
        server.shutdown();server.server_close();worker.join()
    print(json.dumps({'requests':len(requests),'tools_advertised':any(bool(p.get('tools')) for p in requests),'context_sentinel_sent':any('MUST_NOT_LOAD_MODEL_SEARCH' in json.dumps(p) for p in requests),'tool_executed':marker.exists(),'extension_executed':extension_marker.exists(),'session_files':len(list(agent.rglob('*.jsonl'))),'exit_code':proc.returncode,'timeout':timed_out,'scope':'synthetic local HTTP fixture only; no inference engine or real credentials'}))
    assert requests and proc.returncode == 0 and not timed_out, 'CLI fixture did not complete'
    assert not any(p.get('tools') or 'MUST_NOT_LOAD_MODEL_SEARCH' in json.dumps(p) for p in requests), 'Unexpected tools or workspace context'
    assert not marker.exists() and not extension_marker.exists() and not list(root.rglob('*.jsonl')), 'Unexpected execution or session persistence'
