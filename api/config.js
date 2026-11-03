function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Método não permitido' });
  }

  const config = {
    ak: process.env.FIREBASE_API_KEY || '',
    fb: process.env.FIREBASE_DATABASE_URL || '',
    gc: process.env.GOOGLE_CLIENT_ID || '',
  };

  res.setHeader('Content-Type', 'application/javascript; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store, max-age=0');
  return res.status(200).send(`window.CFG0=${JSON.stringify(config)};`);
}

module.exports = handler;
