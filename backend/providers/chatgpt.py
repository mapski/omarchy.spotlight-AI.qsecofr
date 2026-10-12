"""Direct ChatGPT-plan Responses client; no tool dispatcher or agent subprocess."""
from backend.chatgpt_auth import API
from backend.protocol import ResponseEvent, MAX_BYTES
from backend.providers.base import Model, ProviderStatus

class ChatGPTAdapter:
    def __init__(self, auth): self.auth=auth

    def catalog(self, account):
        entries=self.auth.net.json(API+'/models',token=account['access_token']).get('models',[])
        if not isinstance(entries,list): raise ValueError('Invalid catalog')
        return tuple(Model(m['slug'],backend_id=account['handle'],locality='cloud') for m in entries
                     if isinstance(m,dict) and m.get('visibility')=='list' and isinstance(m.get('slug'),str)
                     and 0<len(m['slug'])<=256 and not any(ord(c)<32 for c in m['slug']))

    def discover(self):
        try:
            models=self.catalog(self.auth.snapshot())
            return ProviderStatus('chatgpt',bool(models),'Ready for text Q&A' if models else 'No account models available',models,streaming=True)
        except Exception:
            return ProviderStatus('chatgpt',False,'Continue with ChatGPT, then refresh providers')

    def stream(self, request, cancel):
        if cancel.is_set(): return
        if request.route_id!='chatgpt' or not request.backend_id: raise ValueError('Explicit account required')
        account=self.auth.snapshot(request.backend_id)
        if request.model_id not in {m.id for m in self.catalog(account)}: raise ValueError('Model unavailable')
        items=[*request.history,{'role':'user','content':request.prompt}]
        if any(set(x)!={'role','content'} or x['role'] not in {'user','assistant'} or not isinstance(x['content'],str) for x in items):
            raise ValueError('Text conversation only')
        payload={'model':request.model_id,'input':items,'store':False,'stream':True,
                 'instructions':'Answer the user question. This client supports text answers only and cannot execute tools.'}
        count=0
        for event in self.auth.net.stream(payload,account['access_token'],cancel):
            if cancel.is_set(): return
            kind=event.get('type','')
            if kind in {'error','response.failed','response.incomplete'}: raise ValueError('Response failed')
            item=event.get('item')
            if isinstance(item,dict) and item.get('type') not in {'message','reasoning'}: raise ValueError('Tool response rejected')
            if kind=='response.output_text.delta':
                text=event.get('delta')
                if not isinstance(text,str): raise ValueError('Invalid text')
                count+=len(text.encode())
                if count>MAX_BYTES: raise ValueError('Output limit')
                yield ResponseEvent(request.request_id,'delta',text)
            if kind=='response.completed':
                response=event.get('response',{})
                if response.get('status')!='completed' or response.get('model')!=request.model_id:
                    raise ValueError('Completion or model mismatch')
                if any(x.get('type') not in {'message','reasoning'} for x in response.get('output',[])):
                    raise ValueError('Tool response rejected')
                yield ResponseEvent(request.request_id,'done');return
        if not cancel.is_set(): raise ValueError('Response ended before completion')
