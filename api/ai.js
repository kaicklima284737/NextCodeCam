const RLM = new Map();
const MAX_BODY_BYTES = 4 * 1024 * 1024;
const limited = key => {
  const now = Date.now();
  const recent = (RLM.get(key) || []).filter(t => now - t < 60000);
  recent.push(now);
  RLM.set(key, recent);
  if (RLM.size > 5000) RLM.clear();
  return recent.length > 20;
};

const jsonResponse = (statusCode, payload) => ({
  statusCode,
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload),
});

async function handler(req, res) {
  const method = req?.method || 'GET';
  if (method !== 'POST') {
    if (res && typeof res.status === 'function') {
      return res.status(405).json({ error: 'Método não permitido' });
    }
    return jsonResponse(405, { error: 'Método não permitido' });
  }

  if (!process.env.GEMINI_API_KEY || !process.env.FIREBASE_API_KEY) {
    const payload = { error: 'Servidor sem GEMINI_API_KEY ou FIREBASE_API_KEY' };
    if (res && typeof res.status === 'function') return res.status(500).json(payload);
    return jsonResponse(500, payload);
  }

  const rawBody = req?.body === undefined || req?.body === null ? '' : req.body;
  const bodyText = typeof rawBody === 'string' ? rawBody : JSON.stringify(rawBody || {});
  if (Buffer.byteLength(bodyText, 'utf8') > MAX_BODY_BYTES) {
    const payload = { error: 'Imagem grande demais' };
    if (res && typeof res.status === 'function') return res.status(413).json(payload);
    return jsonResponse(413, payload);
  }

  const authHeader = req?.headers?.authorization || '';
  const token = authHeader.replace('Bearer ', '');

  if (token) {
    const lookup = await fetch(`https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=${process.env.FIREBASE_API_KEY}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ idToken: token }),
    });

    if (!lookup || !lookup.ok) {
      const payload = { error: 'Faça login para usar a IA do servidor' };
      if (res && typeof res.status === 'function') return res.status(401).json(payload);
      return jsonResponse(401, payload);
    }

    const userData = (await lookup.json()).users || [];
    const user = userData[0] || {};
    const okDomains = (process.env.ALLOWED_EMAIL_DOMAINS || '').split(',').map(s => s.trim().toLowerCase()).filter(Boolean);
    const domain = ((user.email || '').split('@')[1] || '').toLowerCase();
    if (okDomains.length && !okDomains.some(d => domain === d || domain.endsWith('.' + d))) {
      const payload = { error: 'E-mail não autorizado para usar a IA' };
      if (res && typeof res.status === 'function') return res.status(403).json(payload);
      return jsonResponse(403, payload);
    }
    if (limited(user.localId || token.slice(-16))) {
      const payload = { error: 'Muitas chamadas. Aguarde um minuto.' };
      if (res && typeof res.status === 'function') return res.status(429).json(payload);
      return jsonResponse(429, payload);
    }
  } else {
    const payload = { error: 'Faça login para usar a IA do servidor' };
    if (res && typeof res.status === 'function') return res.status(401).json(payload);
    return jsonResponse(401, payload);
  }

  let body;
  try {
    if (typeof rawBody === 'string') {
      body = JSON.parse(rawBody || '{}');
    } else if (rawBody && typeof rawBody === 'object') {
      body = rawBody;
    } else {
      body = JSON.parse(bodyText || '{}');
    }
  } catch {
    const payload = { error: 'JSON inválido' };
    if (res && typeof res.status === 'function') return res.status(400).json(payload);
    return jsonResponse(400, payload);
  }

  const model = body.model || 'gemini-2.5-flash';
  if (!/^gemini-[\w.-]+$/.test(model) || !Array.isArray(body.payload?.contents)) {
    const payload = { error: 'Requisição inválida' };
    if (res && typeof res.status === 'function') return res.status(400).json(payload);
    return jsonResponse(400, payload);
  }

  const payload = {
    contents: body.payload.contents,
    generationConfig: {
      responseMimeType: 'application/json',
      temperature: 0.3,
    },
  };

  const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-goog-api-key': process.env.GEMINI_API_KEY,
    },
    body: JSON.stringify(payload),
  });

  const textBody = await response.text();
  if (res && typeof res.status === 'function') {
    res.status(response.status);
    res.setHeader('Content-Type', 'application/json');
    return res.send(textBody);
  }

  return {
    statusCode: response.status,
    headers: { 'Content-Type': 'application/json' },
    body: textBody,
  };
}

module.exports = handler;
module.exports.handler = handler;
module.exports.default = handler;
