# Câmera Acadêmica · NextCode (FIAP)

PWA sem build: câmera, fila de revisão, OCR/IA, pastas automáticas, estudo (resumo, quiz, flashcards), QR seguro, nuvem e grupo.

## Arquivos
`index.html` app · `config.js` suas chaves públicas · `netlify/functions/ai.js` proxy da IA · `_headers` segurança (CSP) · `firebase.rules.json` regras · `sw.js`, `manifest.webmanifest`, `icons/` instalação · `tests/` testes.

## 1. Firebase (gratuito)
1. console.firebase.google.com › criar projeto.
2. Authentication › ative **E-mail/senha** (e Google, se quiser). Em Domínios autorizados, adicione `seu-site.netlify.app`.
3. Realtime Database › criar › aba Regras › cole `firebase.rules.json` › Publicar.
4. Configurações do projeto › copie a **Chave de API da Web** (começa com `AIza`).
5. Preencha `config.js`: `ak` (chave) e `fb` (URL do banco, `https://…firebaseio.com`).
O e-mail precisa ser de um domínio da lista em Mais › QR Code seguro. Inclua o da sua faculdade.

## 2. IA gratuita (Gemini)
- Netlify › Environment variables: `GEMINI_API_KEY` (marque secret, escopo Functions), `FIREBASE_API_KEY` e `ALLOWED_EMAIL_DOMAINS` (ex.: `fiap.com.br`).
- No app: Mais › IA › ligue **IA pelo servidor**.
- Alternativa de teste: cole sua chave em Mais › IA (fica no aparelho).
- Modelo: `gemini-2.5-flash`, com reserva automática `gemini-flash-latest`.

## 3. Publicar (HTTPS obrigatório)
```
npm i -g netlify-cli && netlify login && netlify deploy --prod
```
Após editar arquivos, troque a versão em `sw.js` (`camacad-v3` › `v4`) e publique de novo.

## 4. Galaxy S24 FE
1. Abra o link no Chrome atualizado. 2. Permita câmera e localização. 3. Menu ⋮ › Instalar app.
4. Entre com o e-mail institucional. 5. Mais: IA pelo servidor, importar agenda `.ics`, definir campus.
6. Teste: lousa, documento, QR, lanterna, lentes, zoom, ajuste manual. 7. Sem economia de bateria para o Chrome.
O app detecta recursos na hora (lentes, zoom, lanterna, exposição). Nada é fixo por modelo.

## 5. Como funciona
Captura › **fila de revisão** (área temporária) › análise em segundo plano › você revisa › salva na pasta › sincroniza.
- Lousa/Documento: detecta bordas, corrige perspectiva, uniformiza luz. "Ajustar cantos" corrige à mão.
- Documento: OCR só com bordas detectadas (RN04). "Reanalisar" força.
- Controles manuais desligam a exposição automática até "Reativar IA automática".
- Excluir move para a lixeira (30 dias). Preferências e itens sincronizam entre aparelhos.
- "Enviar foto à IA" desligado: só o texto lido no aparelho vai à IA.

## 6. Limites conhecidos
- ISO direto exige app nativo (Capacitor). O navegador só expõe exposição e foco quando o Chrome permite.
- Cerca de 300 fotos por aparelho. Depois, use PDF da pasta e exclua.
- OCR offline e QR sem Google precisam baixar bibliotecas na 1ª vez. Para uso 100% offline, copie jsQR, Tesseract e jsPDF para a pasta.
- Se a CSP bloquear algo, veja o Console (F12) e ajuste `_headers`.
- Imagens ficam no Realtime Database (reduzidas). Em escala, use Cloud Storage.
- Cotas gratuitas do Gemini e do Firebase mudam.

## 7. Testes
```
pip install playwright && playwright install chromium
python3 tests/qa_browser.py .     # 63 testes, câmera falsa, IA/Firebase simulados
node tests/qa_function.js         # 12 testes da função de IA
```
Não substituem teste em celular real.

## 8. App nativo (opcional)
`npm i @capacitor/core @capacitor/cli && npx cap init CameraAcademica br.fiap.nextcode --web-dir=. && npm i @capacitor/android && npx cap add android`
