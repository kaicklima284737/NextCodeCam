// Proxy da IA: a chave Gemini fica só no servidor.
// Variáveis: GEMINI_API_KEY, FIREBASE_API_KEY e (opcional) ALLOWED_EMAIL_DOMAINS="fiap.com.br,gmail.com"
const RLM=new Map(),limited=k=>{const n=Date.now(),a=(RLM.get(k)||[]).filter(t=>n-t<6e4);a.push(n);RLM.set(k,a);if(RLM.size>5000)RLM.clear();return a.length>20};
const J=(s,o)=>({statusCode:s,headers:{'Content-Type':'application/json'},body:JSON.stringify(o)});
exports.handler=async e=>{
  if(e.httpMethod!=='POST')return J(405,{error:'Método não permitido'});
  if(!process.env.GEMINI_API_KEY||!process.env.FIREBASE_API_KEY)return J(500,{error:'Servidor sem GEMINI_API_KEY ou FIREBASE_API_KEY'});
  if((e.body||'').length>5e6)return J(413,{error:'Imagem grande demais'});
  const tok=(e.headers.authorization||'').replace('Bearer ','');
  const v=tok&&await fetch(`https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=${process.env.FIREBASE_API_KEY}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({idToken:tok})});
  if(!v||!v.ok)return J(401,{error:'Faça login para usar a IA do servidor'});
  const u=((await v.json()).users||[])[0]||{};
  const ok=(process.env.ALLOWED_EMAIL_DOMAINS||'').split(',').map(s=>s.trim().toLowerCase()).filter(Boolean);
  const dom=((u.email||'').split('@')[1]||'').toLowerCase();
  if(ok.length&&!ok.some(d=>dom===d||dom.endsWith('.'+d)))return J(403,{error:'E-mail não autorizado para usar a IA'});
  if(limited(u.localId||tok.slice(-16)))return J(429,{error:'Muitas chamadas. Aguarde um minuto.'});
  let b;try{b=JSON.parse(e.body||'{}')}catch{return J(400,{error:'JSON inválido'})}
  const model=b.model||'gemini-2.5-flash';
  if(!/^gemini-[\w.-]+$/.test(model)||!Array.isArray(b.payload?.contents))return J(400,{error:'Requisição inválida'});
  const payload={contents:b.payload.contents,generationConfig:{responseMimeType:'application/json',temperature:.3}};
  const r=await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`,{method:'POST',headers:{'Content-Type':'application/json','x-goog-api-key':process.env.GEMINI_API_KEY},body:JSON.stringify(payload)});
  return{statusCode:r.status,headers:{'Content-Type':'application/json'},body:await r.text()};
};
