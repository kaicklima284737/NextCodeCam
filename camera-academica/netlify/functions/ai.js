// Proxy da IA: a chave Gemini fica só no servidor (variável GEMINI_API_KEY).
// Exige um usuário Firebase logado (FIREBASE_API_KEY valida o token).
const J=(s,o)=>({statusCode:s,headers:{'Content-Type':'application/json'},body:JSON.stringify(o)});
exports.handler=async e=>{
  if(e.httpMethod!=='POST')return J(405,{error:'Método não permitido'});
  const tok=(e.headers.authorization||'').replace('Bearer ','');
  const v=tok&&await fetch(`https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=${process.env.FIREBASE_API_KEY}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({idToken:tok})});
  if(!v||!v.ok)return J(401,{error:'Faça login para usar a IA do servidor'});
  const{model='gemini-2.5-flash',payload}=JSON.parse(e.body||'{}');
  if(!/^gemini-[\w.-]+$/.test(model)||!payload)return J(400,{error:'Requisição inválida'});
  const r=await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`,{method:'POST',headers:{'Content-Type':'application/json','x-goog-api-key':process.env.GEMINI_API_KEY},body:JSON.stringify(payload)});
  return{statusCode:r.status,headers:{'Content-Type':'application/json'},body:await r.text()};
};
