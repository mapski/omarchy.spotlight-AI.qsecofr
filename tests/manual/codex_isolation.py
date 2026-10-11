"""Manual mock probe: inventory tools without real credentials or inference."""
import argparse,json,os,subprocess,tempfile,threading,signal
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--model', default='gpt-6.1-sol')
parser.add_argument('--disable-question', action='store_true')
parser.add_argument('--require-no-tools', action='store_true')
args = parser.parse_args()

def inventory(request):
 """Include Responses additional_tools and nested namespaces, not just tools."""
 def names(specs, prefix=''):
  for spec in specs:
   name = prefix + spec.get('name', spec.get('type', 'unknown'))
   if spec.get('type') == 'namespace':
    yield from names(spec.get('tools', []), name + '.')
   else:
    yield name
 specs = list(request.get('tools', []))
 for item in request.get('input', []):
  if item.get('type') == 'additional_tools':
   specs.extend(item.get('tools', []))
 return sorted(set(names(specs)))

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
 argv=[str(Path.home()/'.local/share/mise/installs/codex/latest/bin/codex'),'exec','--ignore-user-config','--ignore-rules','--ephemeral','--skip-git-repo-check','--sandbox','read-only','--json','--model',args.model]
 for key,val in {'model_provider':'fixture','model_providers.fixture':{'name':'fixture','base_url':'http://127.0.0.1:'+str(server.server_port)+'/v1','wire_api':'responses','requires_openai_auth':False},'project_doc_max_bytes':0,'web_search':'disabled'}.items():
  if isinstance(val,dict): val='{'+','.join(k+'='+json.dumps(v) for k,v in val.items())+'}'
  else:val=json.dumps(val)
  argv+=['-c',key+'='+val]
 for feature in ['shell_tool','unified_exec','shell_snapshot','hooks','plugins','remote_plugin','skill_search','skill_mcp_dependency_install','view_image','multi_agent','goals','sleep_tool','collaboration_modes','default_mode_request_user_input']:
  argv+=['--disable',feature]
 if args.disable_question:
  argv+=['-c','tools.experimental_request_user_input.enabled=false']
 argv+=['-']
 p=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=project,env={'PATH':os.environ['PATH'],'HOME':str(home),'CODEX_HOME':str(home/'.codex')},text=True,start_new_session=True)
 try:out,err=p.communicate('Synthetic test',timeout=25)
 except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);out,err=p.communicate()
 server.shutdown()
 all_tools = sorted({name for request in requests for name in inventory(request)})
 prompt_files = sum(b'Synthetic test' in path.read_bytes() for path in home.rglob('*') if path.is_file())
 print(json.dumps({'exit':p.returncode,'model':args.model,'question_disabled':args.disable_question,
  'requests':len(requests),'tools':all_tools,
  'top_level_tools':sum(len(x.get('tools',[])) for x in requests),
  'additional_tool_items':sum(i.get('type')=='additional_tools' for x in requests for i in x.get('input',[])),
  'sentinel':any('MUST_NOT_LOAD_MODEL_SEARCH' in json.dumps(x) for x in requests),
  'session_files':len(list(home.rglob('*.jsonl'))),'prompt_files':prompt_files,
  'diagnostic':err[-1800:] if not requests else ''}))
 assert p.returncode == 0 and requests, 'Fixture did not complete'
 assert all(x.get('model') == args.model for x in requests), 'Unexpected model change'
 assert not any('MUST_NOT_LOAD_MODEL_SEARCH' in json.dumps(x) for x in requests)
 assert not list(home.rglob('*.jsonl'))
 assert not prompt_files, 'Synthetic prompt persisted under temporary HOME'
 if args.require_no_tools:
  assert not all_tools, 'Q&A safety gate failed: tools remain exposed'
