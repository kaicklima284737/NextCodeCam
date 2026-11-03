import json,sys,threading,http.server,socketserver,functools,time
from playwright.sync_api import sync_playwright
D=sys.argv[1];PORT=8099
H=functools.partial(http.server.SimpleHTTPRequestHandler,directory=D)
CSP=next(h['value'] for h in json.load(open(D+'/vercel.json'))['headers'][0]['headers'] if h['key']=='Content-Security-Policy')
class Q(H.func):
    def log_message(self,*a):pass
    def end_headers(self):
        self.send_header('Content-Security-Policy',CSP);super().end_headers()
socketserver.TCPServer.allow_reuse_address=True
srv=socketserver.TCPServer(('',PORT),functools.partial(Q,directory=D));threading.Thread(target=srv.serve_forever,daemon=True).start()
U=f'http://localhost:{PORT}/index.html'
R=[]
def wf(pg,expr,timeout=9000):
    t0=time.time()
    while time.time()-t0<timeout/1000:
        if pg.evaluate(expr):return True
        pg.wait_for_timeout(150)
    raise TimeoutError(expr)
def rep(n,ok,d=''):R.append((n,ok));print(('PASS ' if ok else 'FAIL ')+n+(' :: '+str(d)[:110] if d else ''))
def gem(o):return {"candidates":[{"content":{"parts":[{"text":json.dumps(o)}]}}]}
with sync_playwright() as p:
    b=p.chromium.launch(args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream'])
    def mk(cfg=None,init='',ai=None,hold=None,fb=None,raw=None):
        c=b.new_context(permissions=['camera'],service_workers='block',viewport={'width':390,'height':780});pg=c.new_page();pg.errs=[];pg.csp=[];pg.on('console',lambda m:pg.csp.append(m.text) if 'Content Security' in m.text else None)
        pg.on('pageerror',lambda e:pg.errs.append(str(e)));pg.on('dialog',lambda d:d.accept())
        base={'user':{'name':'T'},'key':'K','cons':1}
        base.update(cfg or {})
        pg.add_init_script(f"localStorage.setItem('cfg',{json.dumps(raw if raw else json.dumps(base))});"+init)
        def h(r):
            u=r.request.url
            if u.endswith('/api/config.js'):
                saved=pg.evaluate("JSON.parse(localStorage.getItem('cfg')||'{}')")
                cfgjs=json.dumps({'ak':saved.get('ak',''),'fb':saved.get('fb',''),'gc':''})
                return r.fulfill(body='window.CFG0='+cfgjs+';',content_type='application/javascript')
            if 'generativelanguage' in u:
                if hold is not None:hold.append(r);return
                return r.fulfill(json=gem(ai(r.request.post_data or '') if callable(ai) else ai))
            if 'identitytoolkit' in u:return r.fulfill(status=400,json={'error':{'message':'INVALID_LOGIN_CREDENTIALS'}},headers={'access-control-allow-origin':'*','access-control-allow-headers':'*'})
            if 'securetoken' in u:return r.fulfill(status=400,json={'error':{'message':'TOKEN_EXPIRED'}},headers={'access-control-allow-origin':'*','access-control-allow-headers':'*'})
            if 'firebaseio.com' in u and fb is not None:
                CH={'access-control-allow-origin':'*','access-control-allow-methods':'*','access-control-allow-headers':'*'}
                return r.fulfill(json=fb if r.request.method=='GET' else {},headers=CH)
            if u.startswith('http://localhost'):return r.continue_()
            return r.fulfill(status=200,body='')
        pg.route('**/*',h);pg.goto(U);pg.wait_for_timeout(900);return pg
    def cap(pg):
        for _ in range(6):
            pg.click('#sh');pg.wait_for_timeout(700)
            if pg.evaluate("inbox.length"):break
        wf(pg,"inbox.length&&inbox.every(e=>e.state=='ready'||e.state=='err')");pg.evaluate("openE(inbox[0].id)")
    A1={'title':'Óptica','subject':'Física','topic':'Lentes','text':'Lei de Snell'}
    # T1 XSS grupo
    ev={"x');window.__x=1;//":{'title':'a','folder':'F','sub':'','text':'t','by':'m','ts':1,'thumb':'data:image/jpeg;base64,AA'},
        "k2":{'title':'b','folder':'F','by':'m','ts':2,'thumb':'"><img src=x onerror=window.__y=1>'},
        "ok1":{'title':'legit','folder':'F','sub':'','text':'t','by':'m','ts':3,'thumb':'data:image/jpeg;base64,AA'}}
    pg=mk({'user':{'name':'T','uid':'u','tok':'x','rt':'r','exp':9e15},'fb':'https://t-default-rtdb.firebaseio.com','grp':'ABCDE'},fb=ev);pg.evaluate("go('more')");pg.wait_for_timeout(1200)
    n=pg.locator("#gl button:has-text('Importar')").count()
    for k in range(n):
        try:pg.locator("#gl button:has-text('Importar')").first.click(timeout=1500)
        except Exception:pass
    pg.wait_for_timeout(400);hit=pg.evaluate("window.__x||window.__y")
    rep('XSS via chave/miniatura do grupo',not hit,f"botões={n} itens inválidos bloqueados" if not hit else 'script executou')
    rep('Item de grupo inválido não entra na biblioteca',pg.evaluate("items.length")==1 and pg.evaluate("items[0].id")=='ok1',pg.evaluate("items.map(i=>i.id)"))
    # T2 XSS QR
    pg=mk();pg.evaluate("go('cam');showQR(\"https://edu.br/');window.__q=1;//\")");pg.wait_for_timeout(200)
    try:pg.click("#qrres button.y",timeout=1500)
    except:pass
    pg.wait_for_timeout(200);rep('XSS via URL do QR',not pg.evaluate("window.__q"))
    # T3 descartar durante análise
    hold=[];pg=mk(hold=hold);pg.click('#sh');pg.wait_for_timeout(700);pg.evaluate("openE(inbox[0].id)");pg.click("text=Descartar")
    for r in hold:r.fulfill(json=gem(A1))
    pg.wait_for_timeout(600);rep('Descartar durante análise',not pg.errs,pg.errs[:1])
    # T4 IA sobrescreve campos
    pg=mk(ai=A1);cap(pg);pg.evaluate("save()");pg.wait_for_selector('#v-lib.on')
    pg.evaluate("items[0].sy=1");it=pg.evaluate("items[0].id")
    pg.route('**/generativelanguage*/**',lambda r:r.fulfill(json=gem({'summary':['x'],'folder':'HACK','id':'zz','img':'data:,x'})))
    pg.evaluate(f"act('{it}','summary')");pg.wait_for_timeout(700)
    rep('Resposta da IA só altera campos esperados',pg.evaluate("items[0].folder")=='Física' and pg.evaluate("items[0].id")==it,pg.evaluate("items[0].folder+'|'+items[0].id"))
    # T5 quiz malformado
    pg.route('**/generativelanguage*/**',lambda r:r.fulfill(json=gem({'quiz':[{'q':'?'},{'q':'x','o':'abc'}],'summary':'texto','cards':'x'})))
    pg.evaluate(f"act('{it}','quiz')");pg.wait_for_timeout(600);pg.evaluate(f"act('{it}','summary')");pg.wait_for_timeout(600)
    try:pg.evaluate(f"go('det','{it}');openQ('{it}')")
    except:pass
    pg.wait_for_timeout(500);rep('Formato inesperado da IA não quebra telas',not pg.errs,pg.errs[:1])
    # T6 pasta parecida
    pg=mk(ai={**A1,'subject':'Educação Física'},init="localStorage.setItem('x','1')")
    pg.evaluate("cfg.extra=['Física'];items.push({id:'a',folder:'Física',sub:'',title:'t',text:'',img:'data:,',date:1,sy:1})")
    cap(pg);rep('Educação Física não vira Física',pg.evaluate("st.folder")=='Educação Física',pg.evaluate("st.folder"))
    # T7 duplo salvar + pasta vazia
    pg=mk(ai=A1);cap(pg);pg.evaluate("st.folder='   '");pg.evaluate("Promise.all([save(),save()])");pg.wait_for_timeout(500)
    rep('Salvar 2x / pasta em branco',pg.evaluate("items.length")==1 and pg.evaluate("items[0].folder")!='' and not pg.errs,f"{pg.evaluate('items.length')} itens, pasta='{pg.evaluate('items[0]&&items[0].folder')}' {pg.errs[:1]}")
    # T8 IndexedDB bloqueado
    pg=mk(init="indexedDB.open=()=>{const r={};setTimeout(()=>r.onerror&&r.onerror(new Event('error')),0);return r};")
    rep('App abre com IndexedDB bloqueado',pg.evaluate("!!document.querySelector('.v.on')"))
    # T11 vazamento de câmera
    pg=mk(init="window.__l=0;const g=navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);navigator.mediaDevices.getUserMedia=async c=>{const s=await g(c);s.getTracks().forEach(t=>{window.__l++;const o=t.stop.bind(t);let d=0;t.stop=()=>{if(!d){d=1;window.__l--}o()}});return s};")
    pg.evaluate("go('cam');go('cam')");pg.wait_for_timeout(800);pg.evaluate("go('lib')");pg.wait_for_timeout(500)
    rep('Câmera desliga ao sair da tela',pg.evaluate("window.__l")==0,'trilhas ativas: '+str(pg.evaluate("window.__l")))
    # T12 sair da câmera durante pedido de permissão
    # T13 QR bloqueio
    pg=mk()
    ok=pg.evaluate("[okHost(new URL('https://usp.br@evil.com/')),okHost(new URL('https://usp.br.evil.com')),okHost(new URL('http://usp.br')),okHost(new URL('https://aluno.usp.br')),okHost(new URL('javascript:alert(1)'))]")
    rep('Domínios do QR (esperado F,F,F,T,F)',ok==[False,False,False,True,False],ok)
    # T14 funil básico sem IA
    pg=mk({'key':'','ai':True});cap(pg);rep('Captura sem IA mostra erro claro',pg.evaluate("!!st.err"),pg.evaluate("st.err"))
    rep('Sem erros de JS gerais',not pg.errs,pg.errs[:1])
    pg=mk(ai=lambda *a:{**A1,'subject':'Matematica'});pg.evaluate("items.push({id:'a',folder:'Matemática',sub:'',title:'t',text:'',img:'data:,',date:1,sy:1})");cap(pg)
    rep('Mesma matéria sem acento reutiliza pasta',pg.evaluate("st.folder")=='Matemática',pg.evaluate("st.folder"))
    pg=mk();pg.evaluate("go('cam')");pg.wait_for_timeout(500);pg.click('#bc');pg.wait_for_timeout(200)
    rep('Painel de controles manuais abre',pg.evaluate("!$('#ctl').hidden"));pg.click("#ctl .b.y");pg.wait_for_timeout(200)
    rep('Reativar IA automática fecha o painel',pg.evaluate("$('#ctl').hidden")and not pg.errs,pg.errs[:1])
    pg=mk({'user':{'name':'T','uid':'u','tok':'x','rt':'r','exp':9e15},'fb':'https://t-default-rtdb.firebaseio.com'},fb={})
    pg.evaluate("items.push({id:'z',folder:'F',sub:'',title:'t',text:'',img:'data:image/jpeg;base64,AA',date:1})");
    rep('Biblioteca mostra pendência de nuvem',pg.evaluate("go('lib'),$('#v-lib').innerText.includes('pendente')"))
    pg=mk(ai=A1,cfg={'cons':0});pg.on('dialog',lambda d:None)
    pg.evaluate("go('cam')");pg.wait_for_timeout(500)
    # --- rodada 2: HTML/aspas em pasta local, tombstone, monkey ---
    reqs=[]
    pg=mk({'user':{'name':'T','uid':'u','tok':'x','rt':'r','exp':9e15},'fb':'https://t-default-rtdb.firebaseio.com'},fb={},ai=A1)
    pg.on('request',lambda r:reqs.append((r.method,r.url)) if 'firebaseio.com' in r.url else None)
    pg.evaluate("items.push({id:'e1',folder:'\\'\"><img src=x onerror=window.__z=1>',sub:'\"><svg onload=window.__z=1>',title:'<b>x</b>',text:'<script>window.__z=1<\\/script>',img:'data:image/jpeg;base64,AA',date:1,sy:1});go('lib')");pg.wait_for_timeout(300)
    pg.evaluate("pf(0)");pg.evaluate("go('det','e1')");pg.evaluate("go('more')");pg.wait_for_timeout(300)
    rep('HTML/aspas em nomes locais não executam',not pg.evaluate("window.__z"))
    pg.evaluate("purge('e1')");pg.wait_for_timeout(1500)
    rep('Exclusão envia marcador à nuvem',any(m=='PUT' and '/dels/e1' in u for m,u in reqs) and any(m=='DELETE' for m,u in reqs),[m for m,u in reqs][:6])
    import random;random.seed(7)
    pg=mk(ai=A1);pg.evaluate("go('cam')");pg.wait_for_timeout(500)
    sel="button:visible,nav button,.it:visible,.fc:visible,.ch:visible,.op:visible"
    for k in range(140):
        try:
            els=pg.locator(sel);n=els.count()
            if n:els.nth(random.randrange(n)).click(timeout=400,force=True)
        except Exception:pass
        if k%25==0:pg.wait_for_timeout(300)
    pg.wait_for_timeout(800)
    rep('Teste de cliques aleatórios (140 cliques)',not pg.errs,pg.errs[:2])
    # --- rodada 3 ---
    def lg(email):
        pg=mk({'user':None,'ak':'AIzaTEST'});pg.click("text=Entrar com e-mail institucional");pg.fill("input[name=e]",email);pg.fill("input[name=p]","123456");pg.click("#lf .b.y");pg.wait_for_timeout(500);return pg.evaluate("$('#toast').textContent")
    m=lg('aluno@fiap.com.br');rep('Login inválido mostra mensagem clara',m=='E-mail ou senha inválidos',m)
    m=lg('x@gmail.com');rep('E-mail não institucional é recusado',m=='Use seu e-mail institucional',m)
    pg=mk({'user':{'name':'T','uid':'u','tok':'x','rt':'r','exp':1},'ak':'AIzaTEST','fb':'https://t-default-rtdb.firebaseio.com'},fb={});pg.evaluate("tok()");pg.wait_for_timeout(500)
    rep('Sessão expirada volta ao login',pg.evaluate("cfg.user===null && $('#v-login').classList.contains('on')"))
    calls=[]
    def aiq(body):
        calls.append(1);return {'quiz':[{'q':'Q?','o':['a','b','c','d'],'a':1,'e':'porque'}],**A1}
    pg=mk(ai=aiq);pg.evaluate("setMode('doc')");cap(pg);n0=len(calls)
    rep('Modo Documento: OCR só após bordas (RN04)',pg.evaluate("st.rect")or(pg.evaluate("!!st.err")and n0==0),f"rect={pg.evaluate('st.rect')} chamadasIA={n0}")
    pg.evaluate("analyze(st,1)");pg.wait_for_timeout(700);rep('Reanalisar força a IA',len(calls)>n0 or pg.evaluate("!!st.text"),len(calls))
    pg.evaluate("st.folder='Física'");pg.evaluate("save()");pg.wait_for_timeout(400);iid=pg.evaluate("items[0].id")
    pg.evaluate(f"go('det','{iid}')")
    with pg.expect_download(timeout=4000) as d:pg.click("text=Exportar TXT")
    rep('Exporta TXT',d.value.suggested_filename.endswith('.txt'),d.value.suggested_filename)
    pg.click("text=Exportar PDF");pg.wait_for_timeout(800);rep('PDF sem internet não quebra',not pg.errs,pg.errs[:1])
    pg.evaluate(f"openQ('{iid}')");pg.wait_for_timeout(900)
    rep('Quiz é gerado e exibido',pg.evaluate("$('#v-quiz').innerText.includes('Questão 1 de 1')"))
    pg.click("#v-quiz .op >> nth=1");pg.wait_for_timeout(200)
    rep('Quiz corrige a resposta',pg.evaluate("$('#v-quiz').innerText.includes('Resultado: 1 de 1')"))
    pg.evaluate("thm();thm();F.q='(*[\\\\';go('lib')");pg.evaluate("setGrp&&($('#gc')&&0)")
    ov=[]
    for v in ['lib','more','quiz','cam']:
        pg.evaluate(f"go('{v}')");pg.wait_for_timeout(250);ov.append((v,pg.evaluate("(e=>e.scrollWidth-e.clientWidth)(document.querySelector('.v.on'))")))
    rep('Sem rolagem horizontal nas telas',all(x<=1 for _,x in ov),ov)
    rep('Tema e busca com símbolos sem erro',not pg.errs,pg.errs[:1])
    pg=mk({'user':{'name':'T','uid':'u','tok':'x','rt':'r','exp':9e15},'fb':'https://t-default-rtdb.firebaseio.com','ai':True},fb={})
    pg.route('**/users/u/prefs.json*',lambda r:r.fulfill(json={'ai':False,'sched':'seg 19:00-22:00 Física','model':'x/../y','org':'sim'},headers={'access-control-allow-origin':'*'}))
    pg.evaluate("LASTP='';sync()");pg.wait_for_timeout(900)
    rep('Preferências voltam da nuvem (só valores válidos)',pg.evaluate("cfg.ai===false&&cfg.sched.includes('Física')&&cfg.org===true&&cfg.model=='gemini-2.5-flash'"),pg.evaluate("[cfg.ai,cfg.org,cfg.model]"))
    pg.evaluate("go('more')");pg.click("text=Restaurar padrões");pg.wait_for_timeout(300)
    rep('Restaurar padrões',pg.evaluate("cfg.ai===true&&cfg.sched==''")and not pg.errs,pg.errs[:1])
    # ===== rodada 4: ataques e fluxos reais =====
    CORS={'access-control-allow-origin':'*','access-control-allow-headers':'*','access-control-allow-methods':'*'}
    pg=mk(raw=json.dumps({'ai':'sim','extra':'x','dels':5,'model':'../x','user':5,'mode':'evil','dom':None,'hq':'x'}))
    rep('Config corrompida não derruba o app',pg.evaluate("!!document.querySelector('.v.on')&&cfg.mode=='foto'&&Array.isArray(cfg.extra)&&cfg.ai===true&&/^gemini-/.test(cfg.model)")and not pg.errs,pg.errs[:1])
    pg=mk();pg.evaluate("idb('put','items',[null,'x',5,{id:\"a'b\",img:'data:image/jpeg;base64,AA'},{id:'ok1',img:'data:image/jpeg;base64,AA',title:'<img src=x onerror=window.__z=1>',folder:'F'},{id:'ok2',img:'javascript:alert(1)'}])");pg.evaluate("idb('put','inbox',[null,{id:'q1',img:'data:image/jpeg;base64,AA',state:'busy',title:'<b>'},{id:\"x'y\",img:'data:image/jpeg;base64,AA'}])");pg.wait_for_timeout(300)
    pg.reload();pg.wait_for_timeout(900);pg.evaluate("go('lib');openE('q1')");pg.wait_for_timeout(300)
    rep('Banco local corrompido é saneado',pg.evaluate("items.length==1&&inbox.length==1&&!window.__z")and not pg.errs,(pg.evaluate("[items.length,inbox.length]"),pg.errs[:1]))
    hold=[];pg=mk(hold=hold);pg.evaluate("AIMS=300");pg.click('#sh');wf(pg,"inbox.length&&inbox[0].state=='err'",6000)
    rep('IA travada vira erro com tempo limite',pg.evaluate("inbox[0].err").startswith('A IA demorou'),pg.evaluate("inbox[0].err"))
    pg.evaluate("AIMS=45000");pg.unroute('**/*');pg.route('**/*',lambda r:r.fulfill(json=gem(A1),headers=CORS) if 'generativelanguage' in r.request.url else (r.continue_() if r.request.url.startswith('http://localhost') else r.fulfill(status=200,body='')))
    pg.evaluate("dispatchEvent(new Event('online'))");wf(pg,"inbox[0].state=='ready'",6000);rep('Ao voltar a internet a fila é reanalisada',True)
    pg=mk({'user':{'name':'T','uid':'u','tok':'x','rt':'r','exp':9e15},'fb':'https://t-default-rtdb.firebaseio.com'},fb={'__proto__':{'folder':'HACK','img':'data:image/jpeg;base64,AA'},'constructor':{'img':'data:image/jpeg;base64,AA'}})
    pg.evaluate("LASTP='';sync()");pg.wait_for_timeout(700);rep('Chaves __proto__/constructor da nuvem não poluem nada',pg.evaluate("({}).folder===undefined&&Object.prototype.folder===undefined")and not pg.errs,pg.errs[:1])
    pg=mk();pg.evaluate("go('cam')");pg.wait_for_timeout(300)
    pg.set_input_files('#gal',files=[{'name':'big.jpg','mimeType':'image/jpeg','buffer':b'0'*31_000_000},{'name':'x.txt','mimeType':'text/plain','buffer':b'oi'},{'name':'lixo.jpg','mimeType':'image/jpeg','buffer':b'naoeimagem'},{'name':'v.svg','mimeType':'image/svg+xml','buffer':b'<svg xmlns="http://www.w3.org/2000/svg"><script>window.__s=1</script></svg>'}]);pg.wait_for_timeout(1500)
    rep('Arquivos gigantes, falsos ou SVG são rejeitados',pg.evaluate("inbox.length==0&&!window.__s")and not pg.errs,(pg.evaluate("inbox.length"),pg.errs[:1]))
    pg=mk(ai=A1);pg.evaluate("go('cam')");pg.wait_for_timeout(300);pg.evaluate("for(let i=0;i<25;i++)snap()");pg.wait_for_timeout(2500)
    rep('Disparo repetido não quebra nem passa de 60',pg.evaluate("inbox.length<=60")and not pg.errs,(pg.evaluate("inbox.length"),pg.errs[:1]))
    pg=mk(ai=A1);pg.evaluate("setMode('lousa')");cap(pg);pg.click("text=Ajustar cantos");pg.wait_for_selector('#adj');pg.click('#ao');pg.wait_for_timeout(500)
    rep('Ajuste manual de cantos aplica o recorte',pg.evaluate("!document.querySelector('#adj')&&st.rect")and not pg.errs,pg.errs[:1])
    pg=mk(ai=A1);cap(pg);pg.evaluate("st.title='<img src=x onerror=window.__t=1>';st.folder='\"><svg onload=window.__t=1>';rRev();st=null;rRev()");pg.wait_for_timeout(200)
    rep('HTML na fila de revisão não executa',not pg.evaluate("window.__t"))
    pg=mk({'auto':True},ai=A1);pg.click('#sh');wf(pg,"items.length==1&&inbox.length==0",8000);rep('Salvar sem revisar guarda direto',True)
    pg=mk({'rev':True},ai=A1)
    for _ in range(6):
        pg.click('#sh');pg.wait_for_timeout(700)
        if pg.evaluate("inbox.length"):break
    rep('Abrir revisão após cada foto',pg.evaluate("$('#v-rev').classList.contains('on')"),pg.evaluate("[cur,inbox.length,cfg.rev]"))
    pg=mk(ai=A1);pg.click('#sh');wf(pg,"inbox.length==1&&inbox[0].state=='ready'");pg.click('#sh');wf(pg,"inbox.length==2&&inbox.every(e=>e.state=='ready')");pg.evaluate("go('rev')");pg.click("text=Salvar 2 prontos");pg.wait_for_timeout(600)
    rep('Várias fotos em sequência e salvar todas',pg.evaluate("items.length==2&&inbox.length==0"),pg.evaluate("[items.length,inbox.length]"))
    pg=mk();pg.evaluate("items.push({id:'c1',folder:'F',sub:'',title:'t',text:'x',img:'data:image/jpeg;base64,AA',date:1,sy:1,cards:[{f:'a',v:'b',b:0,d:0},{f:'c',v:'d',b:0,d:0}]});study()");pg.wait_for_timeout(200)
    pg.click("#v-study .b.y");c=pg.evaluate("items[0].cards[0]");pg.click("#v-study .b.d");c2=pg.evaluate("items[0].cards[1]")
    rep('Flashcards: lembrei agenda; revisar volta à fila',c['b']==1 and c['d']>time.time()*1000 and c2['b']==0 and pg.evaluate("FS.q.length")==1,(c,c2))
    pg=mk();r=pg.evaluate("ics('BEGIN:VEVENT\\r\\nDTSTART;TZID=America/Sao_Paulo:20260302T190000\\r\\nDTEND;TZID=America/Sao_Paulo:20260302T220000\\r\\nRRULE:FREQ=WEEKLY;BYDAY=MO,WE\\r\\nSUMMARY:Engenharia de Software\\r\\nEND:VEVENT')")
    rep('Importa agenda .ics',r.split('\n')==['seg 19:00-22:00 Engenharia de Software','qua 19:00-22:00 Engenharia de Software'],r)
    pg=mk();pg.evaluate("items.push({id:'d1',folder:'F',sub:'',title:'t',text:'',img:'data:image/jpeg;base64,AA',date:1,sy:1});del('d1')");pg.wait_for_timeout(200)
    a=pg.evaluate("vis().length");pg.evaluate("go('more')");bq=pg.evaluate("$('#v-more').innerText.includes('Restaurar')");pg.evaluate("rest('d1')");rep('Lixeira: exclui e restaura',a==0 and bq and pg.evaluate("vis().length")==1,(a,bq))
    pg=mk({'user':{'name':'T','uid':'u','tok':'x','rt':'r','exp':9e15},'ak':'AIza','fb':'https://t-default-rtdb.firebaseio.com'},fb={});pg.route('**/identitytoolkit.googleapis.com/**',lambda r:r.fulfill(json={},headers=CORS))
    pg.evaluate("items.push({id:'w1',folder:'F',sub:'',title:'t',text:'',img:'data:image/jpeg;base64,AA',date:1,sy:1})");pg.evaluate("wipe()");pg.wait_for_timeout(800)
    rep('Apagar meus dados limpa aparelho e sessão',pg.evaluate("items.length==0&&cfg.user===null"),pg.evaluate("[items.length,cfg.user]"))
    pg=mk({'model':'gemini-bogus'});pg.route('**/generativelanguage*/**',lambda r:r.fulfill(status=404,json={'error':{'message':'models/gemini-bogus is not found'}},headers=CORS) if 'bogus' in r.request.url else r.fulfill(json=gem(A1),headers=CORS));cap(pg)
    rep('Modelo inexistente cai para modelo de reserva',pg.evaluate("st.state")=='ready',pg.evaluate("st.err"))
    S24="""MediaStreamTrack.prototype.getCapabilities=function(){return{exposureCompensation:{min:-2,max:2,step:.5},torch:true,zoom:{min:1,max:10,step:.1},focusDistance:{min:0,max:1,step:.01},focusMode:['manual','continuous'],exposureMode:['continuous','manual']}};window.__ac=[];MediaStreamTrack.prototype.applyConstraints=function(c){window.__ac.push(JSON.stringify(c));return Promise.resolve()};navigator.mediaDevices.enumerateDevices=async()=>[1,2,3].map(i=>({kind:'videoinput',label:'camera2 '+i+', facing back',deviceId:'d'+i}));"""
    pg=mk(init=S24);pg.wait_for_timeout(900);pg.click('#bc');pg.wait_for_timeout(200)
    rep('Aparelho com lanterna, 3 lentes, zoom e foco manual',pg.evaluate("!$('#bt').hidden&&!$('#bl').hidden&&$$('#ctl input[type=range]').length>=2&&window.__ac.some(x=>x.includes('continuous'))"),pg.evaluate("[$('#bt').hidden,$('#bl').hidden,$$('#ctl input[type=range]').length,window.__ac.length]"))
    rep('CSP não bloqueou nada do app',not any(('connect' in x or 'script' in x) and 'firebaseio' not in x for x in pg.csp),pg.csp[:1])
    # ===== rodada 5: persistência e sincronização =====
    puts=[]
    pg=mk({'user':{'name':'T','uid':'u','tok':'x','rt':'r','exp':9e15},'fb':'https://t-default-rtdb.firebaseio.com'},fb={},init="window.__p=0;const op=IDBObjectStore.prototype.put;IDBObjectStore.prototype.put=function(){window.__p++;return op.apply(this,arguments)};")
    pg.evaluate("for(let i=0;i<30;i++)items.push({id:'m'+i,folder:'F',sub:'',title:'t'+i,text:'x',img:'data:image/jpeg;base64,'+'A'.repeat(4000),date:i,sy:1,up:1})");pg.evaluate("sv2()");pg.wait_for_timeout(800)
    pg.evaluate("window.__p=0;items[3].title='novo';touch(items[3]);sv2()");pg.wait_for_timeout(500)
    rep('Editar 1 item grava só esse registro (não a biblioteca toda)',pg.evaluate("window.__p")<=8,pg.evaluate("window.__p"))
    pg.reload();pg.wait_for_timeout(1000);rep('Biblioteca por registro volta após reiniciar',pg.evaluate("items.length")==30 and pg.evaluate("items.some(i=>i.title=='novo')"),pg.evaluate("items.length"))
    pg.evaluate("purge('m5')");pg.wait_for_timeout(500);pg.reload();pg.wait_for_timeout(900);rep('Excluir definitivo remove o registro',pg.evaluate("items.length")==29)
    reqs=[]
    pg=mk({'user':{'name':'T','uid':'u','tok':'x','rt':'r','exp':9e15},'fb':'https://t-default-rtdb.firebaseio.com'},fb={})
    pg.on('request',lambda r:reqs.append((r.method,r.url)) if 'firebaseio' in r.url else None)
    pg.evaluate("items.push({id:'bad1',folder:'F',sub:'',title:'ruim',text:'',img:'data:image/jpeg;base64,AA',date:2,sy:0},{id:'good1',folder:'F',sub:'',title:'bom',text:'',img:'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==',date:3,sy:0})");pg.evaluate("sync()");pg.wait_for_timeout(1500)
    rep('Item com imagem corrompida não trava a sincronização',any(m=='PUT' and '/items/good1' in u for m,u in reqs) and not any('/items/bad1' in u for m,u in reqs),[u[-20:] for m,u in reqs if m=='PUT'][:4])
    pg=mk({'user':{'name':'T','uid':'u','tok':'x','rt':'r','exp':9e15},'fb':'https://evil.example.com'},fb={});rep('URL de banco que não é Firebase é recusada',pg.evaluate("okFb()===false&&canSync()===false"))
    # ===== rodada 6: escala e permissões =====
    pg=mk()
    pg.evaluate("for(let i=0;i<150;i++)items.push({id:'s'+i,folder:'F',sub:'',title:'t'+i,text:'x',img:'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==',date:i,sy:1})");pg.evaluate("go('lib')");pg.wait_for_timeout(600)
    rep('Biblioteca grande mostra 60 e carrega mais',pg.evaluate("$$('#lst .it').length")==60 and pg.evaluate("!$('#lm').hidden"),pg.evaluate("$$('#lst .it').length"));pg.click('#lm');rep('Mostrar mais carrega +60',pg.evaluate("$$('#lst .it').length")==120)
    pg.evaluate("backfill()");pg.wait_for_timeout(1500);rep('Miniaturas geradas em segundo plano',pg.evaluate("items.every(i=>typeof i.th=='string')"))
    pg=mk(init="navigator.mediaDevices.getUserMedia=()=>Promise.reject(new DOMException('x','NotAllowedError'));")
    pg.evaluate("go('cam')");pg.wait_for_timeout(500);rep('Câmera negada mostra alternativa sem quebrar',pg.evaluate("!$('#nocam').hidden")and not pg.errs,pg.errs[:1])
    with pg.expect_file_chooser(timeout=3000) as fc:pg.click('#sh')
    rep('Disparo sem câmera abre a câmera do sistema',fc.value is not None)
    pg=mk(init="Object.defineProperty(navigator,'mediaDevices',{value:undefined});");pg.evaluate("go('cam')");pg.wait_for_timeout(400)
    rep('Contexto sem mediaDevices (HTTP) não quebra',pg.evaluate("!$('#nocam').hidden")and not pg.errs,pg.errs[:1])
    b.close()
print('RESUMO',sum(1 for _,o in R if o),'/',len(R))
