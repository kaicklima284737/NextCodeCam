# Câmera Acadêmica · NextCode (FIAP)

PWA sem build: câmera, fila de revisão, OCR/IA, pastas automáticas, estudo (resumo, quiz, flashcards), QR seguro, nuvem e grupo.

## Arquivos
`index.html` app · `api/config.js` fornece a configuração pública do Firebase a partir das variáveis de ambiente · `api/ai.js` proxy da IA · `.env.example` lista os nomes das variáveis sem valores · `vercel.json` configuração da Vercel e cabeçalhos de segurança (CSP) · `firebase.rules.json` regras · `sw.js`, `manifest.webmanifest`, `icons/` instalação · `tests/` testes.

## 1. Firebase (gratuito)
1. console.firebase.google.com › criar projeto.
2. Authentication › ative **E-mail/senha** (e Google, se quiser). Em Domínios autorizados, adicione o domínio Vercel do projeto (por exemplo, `seu-projeto.vercel.app`) e qualquer domínio personalizado usado.
3. Realtime Database › criar › aba Regras › cole `firebase.rules.json` › Publicar.
4. Configurações do projeto › copie a **Chave de API da Web** e a URL do Realtime Database.
5. Adicione `FIREBASE_API_KEY` e `FIREBASE_DATABASE_URL` às variáveis de ambiente da Vercel. O endpoint `api/config.js` fornece esses valores ao app; não os grave em `index.html`, `config.js` ou no Git.
O e-mail precisa ser de um domínio da lista em Mais › QR Code seguro. Inclua o da sua faculdade.

## 2. IA gratuita (Gemini)
- Vercel › Settings › Environment Variables: adicione `GEMINI_API_KEY` como segredo e `ALLOWED_EMAIL_DOMAINS` (ex.: `fiap.com.br`). `FIREBASE_API_KEY` também é lida pela função para validar sessões. Selecione os ambientes em que a IA será usada (Production, Preview e/ou Development) e faça um novo deploy após alterar variáveis.
- No app: Mais › IA › ligue **IA pelo servidor**.
- Alternativa de teste: cole sua chave em Mais › IA (fica no armazenamento local do navegador; não a compartilhe nem use em aparelhos compartilhados).
- Modelo: `gemini-2.5-flash`, com reserva automática `gemini-flash-latest`.

## 3. Variáveis e chaves
Adicione estas variáveis em Vercel › Settings › Environment Variables; `.env.example` contém apenas os nomes, sem credenciais:

| Variável | Uso | Exposição |
| --- | --- | --- |
| `GEMINI_API_KEY` | Chamada Gemini pelo proxy do servidor | Segredo; nunca é enviado ao navegador |
| `FIREBASE_API_KEY` | Login Firebase e validação de sessão | Chave web pública; o app precisa recebê-la no navegador. Restrinja-a por domínio HTTP e APIs no Google Cloud |
| `FIREBASE_DATABASE_URL` | Endereço do Realtime Database | Configuração pública |
| `ALLOWED_EMAIL_DOMAINS` | Restringe quem pode usar o proxy de IA | Configuração do servidor |
| `GOOGLE_CLIENT_ID` | Login Google opcional | Identificador público |

O nome `FIREBASE_API_KEY` é compartilhado entre Firebase e o proxy. Apesar de ser configurada na Vercel, essa chave web não é um segredo e fica visível para usuários do app; a segurança depende das restrições da chave, Firebase Authentication e regras do banco. A chave secreta do Gemini não é retornada pelo endpoint público.

## 4. Publicar (HTTPS obrigatório)
1. Importe este repositório na Vercel, mantenha a raiz do projeto como diretório raiz e use o preset **Other**. Não é necessário comando de build: o app é estático e `api/ai.js` é implantada como função serverless.
2. Configure as variáveis de ambiente da IA conforme a seção anterior. A IA também pode ser usada com uma chave própria no aparelho sem essas variáveis.
3. Publique pelo painel da Vercel ou com `npx vercel --prod`. A URL `/api/ai` é atendida pela função em `api/ai.js` (limite de execução configurado para 60 segundos); os demais arquivos estáticos e cabeçalhos estão configurados em `vercel.json`.
4. Após editar arquivos, troque a versão em `sw.js` (`camacad-v3` › `v4`) e publique de novo.

## 5. Galaxy S24 FE
1. Abra o link no Chrome atualizado. 2. Permita câmera e localização. 3. Menu ⋮ › Instalar app.
4. Entre com o e-mail institucional. 5. Mais: IA pelo servidor, importar agenda `.ics`, definir campus.
6. Teste: lousa, documento, QR, lanterna, lentes, zoom, ajuste manual. 7. Sem economia de bateria para o Chrome.
O app detecta recursos na hora (lentes, zoom, lanterna, exposição). Nada é fixo por modelo.

## 6. Como funciona
Captura › **fila de revisão** (área temporária) › análise em segundo plano › você revisa › salva na pasta › sincroniza.
- Lousa/Documento: detecta bordas, corrige perspectiva, uniformiza luz. "Ajustar cantos" corrige à mão.
- Documento: OCR só com bordas detectadas (RN04). "Reanalisar" força.
- Controles manuais desligam a exposição automática até "Reativar IA automática".
- Excluir move para a lixeira (30 dias). Preferências e itens sincronizam entre aparelhos.
- "Enviar foto à IA" desligado: só o texto lido no aparelho vai à IA.

## 7. Limites conhecidos
- ISO direto exige app nativo (Capacitor). O navegador só expõe exposição e foco quando o Chrome permite.
- Cerca de 300 fotos por aparelho. Depois, use PDF da pasta e exclua.
- OCR offline e QR sem Google precisam baixar bibliotecas na 1ª vez. Para uso 100% offline, copie jsQR, Tesseract e jsPDF para a pasta.
- Se a CSP bloquear algo, veja o Console (F12) e ajuste os cabeçalhos em `vercel.json`.
- Imagens ficam no Realtime Database (reduzidas). Em escala, use Cloud Storage.
- Cotas gratuitas do Gemini e do Firebase mudam.

## 8. Testes
```
pip install playwright && playwright install chromium
python3 tests/qa_browser.py .     # 63 testes, câmera falsa, IA/Firebase simulados
node tests/qa_function.js         # 12 testes da função de IA
```
Não substituem teste em celular real.

## 9. App nativo (opcional)
`npm i @capacitor/core @capacitor/cli && npx cap init CameraAcademica br.fiap.nextcode --web-dir=. && npm i @capacitor/android && npx cap add android`
