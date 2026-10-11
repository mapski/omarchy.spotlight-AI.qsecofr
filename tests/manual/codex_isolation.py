"""Manual mock probe: inventory tools without real credentials or inference."""
import json,os,shutil,subprocess,tempfile,threading,signal
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp); home=root/'home';home.mkdir();(home/'.codex').mkdir(); project=root/'project';project.mkdir()
 (project/'AGENTS.md').write_text('MUST_NOT_LOAD_MODEL_SEARCH')
 requests=[]
 class Handler(BaseHTTPRequestHandler):
  def log_message(self,*args):pass
  def do_POST(self):
   requests.append(json.loads(self.rfile.read(int(self.headers['Content-Length']))))
   self.send_response(200);self.send_header('Content-Type','text/event-stream');self.end_headers()
   msg={'id':'msg_1','type':'message','role':'assistant','status':'completed','content':[{'type':'output_text','text':'Synthetic response','annotations':[]}]}
   for ev in [{'type':'response.created','response':{'id':'resp_1','status':'in_progress','output':[]}}, {'type':'response.output_item.done','output_index':0,'item':msg},{'type':'response.completed','response':{'id':'resp_1','status':'completed','output':[msg],'usage':{'input_tokens':1,'output_tokens':1,'total_tokens':2}}}]:
    self.wfile.write(('data: '+json.dumps(ev)+'\n\n').encode())
 server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 argv=[str(Path.home()/'.local/share/mise/installs/codex/latest/bin/codex'),'exec','--ignore-user-config','--ignore-rules','--ephemeral','--skip-git-repo-check','--sandbox','read-only','--json','--model','synthetic']
 for key,val in {'model_provider':'fixture','model_providers.fixture':{'name':'fixture','base_url':'http://127.0.0.1:'+str(server.server_port)+'/v1','wire_api':'responses','requires_openai_auth':False},'project_doc_max_bytes':0,'web_search':'disabled'}.items():
  if isinstance(val,dict): val='{'+','.join(k+'='+json.dumps(v) for k,v in val.items())+'}'
  else:val=json.dumps(val)
  argv+=['-c',key+'='+val]
 for feature in ['shell_tool','unified_exec','shell_snapshot','hooks','plugins','remote_plugin','skill_search','skill_mcp_dependency_install','view_image','multi_agent','goals','sleep_tool','collaboration_modes','default_mode_request_user_input']:
  argv+=['--disable',feature]
 argv+=['-']
 p=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=project,env={'PATH':os.environ['PATH'],'HOME':str(home),'CODEX_HOME':str(home/'.codex')},text=True,start_new_session=True)
 try:out,err=p.communicate('Synthetic test',timeout=25)
 except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);out,err=p.communicate()
 server.shutdown()
 print(json.dumps({'exit':p.returncode,'requests':len(requests),'tools':[t.get('name',t.get('type')) for t in requests[0].get('tools',[])] if requests else None,'sentinel':any('MUST_NOT_LOAD_MODEL_SEARCH' in json.dumps(x) for x in requests),'session_files':len(list(home.rglob('*.jsonl'))),'diagnostic':err[-1800:] if not requests else ''}))

 # This inventory intentionally records the remaining request_user_input tool.
 assert p.returncode == 0 and requests, 'Fixture did not complete'
 assert not any('MUST_NOT_LOAD_MODEL_SEARCH' in json.dumps(x) for x in requests)
 assert not list(home.rglob('*.jsonl'))
 assert all(t.get('name') == 'request_user_input' for x in requests for t in x.get('tools', [])), 'Unexpected tool inventory'
