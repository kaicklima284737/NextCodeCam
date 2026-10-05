# Câmera Acadêmica · NextCode (FIAP · Sprint 2)

PWA sem build (HTML + JS puro): câmera nativa, correção de perspectiva, OCR, resumo, quiz, flashcards,
pastas automáticas por IA, QR seguro, login real, backup na nuvem e grupo de estudo.

## Arquivos
| Arquivo | Função |
|---|---|
| `index.html` | App completo |
| `config.js` | **Você preenche:** chave Firebase, URL do banco, Client ID Google |
| `netlify/functions/ai.js` | Proxy da IA (a chave Gemini fica só no servidor) |
| `netlify.toml`, `_headers` | Configuração de hospedagem |
| `firebase.rules.json` | Regras do banco (dados por usuário + grupos) |
| `manifest.webmanifest`, `icons/`, `sw.js` | Instalação e uso offline |

## Passo 1 · Firebase (login + nuvem + grupo), plano gratuito
1. console.firebase.google.com › Criar projeto.
2. **Authentication** › Método de login › ative **E-mail/senha** (e **Google**, se quiser).
3. **Realtime Database** › Criar banco › aba Regras › cole `firebase.rules.json` › Publicar.
4. **Configurações do projeto** › copie a *Chave de API da Web*.
5. Abra `config.js` e preencha `ak` (chave) e `fb` (URL do banco).
6. Google (opcional): Google Cloud Console › APIs e serviços › Credenciais › ID do cliente OAuth (Web); em "Origens JavaScript autorizadas" coloque o endereço do seu site. Cole o ID em `gc`. No Firebase, em Authentication › Google, informe o mesmo Client ID.
7. Authentication › Configurações › Domínios autorizados: adicione o domínio do seu site.

O cadastro por e-mail só aceita domínios da lista de "Domínios permitidos" (Mais › QR Code seguro); inclua o da sua instituição.

## Passo 2 · IA gratuita (Gemini), duas formas
- **Rápida (protótipo):** chave de aistudio.google.com/apikey colada em Mais › IA. Fica no aparelho.
- **Segura (recomendada):** no Netlify, Site settings › Environment variables: `GEMINI_API_KEY` e `FIREBASE_API_KEY`. Depois ligue **IA pelo servidor** em Mais › IA. Só usuários logados chamam a função.
Sem IA, o app faz OCR local (Tesseract.js), sem resumo, quiz nem classificação.

## Passo 3 · Publicar (HTTPS é obrigatório para a câmera)
- **Só o app (sem IA pelo servidor):** arraste a pasta em app.netlify.com/drop.
- **App + função de IA:** use Git ou a CLI:
  ```
  npm i -g netlify-cli && netlify login && netlify deploy --prod
  ```
- Local: `python3 -m http.server 8080` e abra `http://localhost:8080`.
Android: menu › Instalar app. iPhone: Compartilhar › Adicionar à Tela de Início.

## Como funciona
Captura › **área temporária de revisão** › IA analisa › você decide › salva na pasta › sincroniza.
- **Lousa/Documento:** detecta o quadrilátero, corrige a perspectiva (homografia), normaliza luz e sombra (reduz reflexo difuso) e ajusta contraste. No modo Documento, o OCR só roda se as bordas retangulares forem detectadas (RN04); "Reanalisar" força.
- **Nuvem (HU9):** cada item é salvo em `users/<uid>/items`. Envio automático, em segundo plano, a cada edição, ao voltar a conexão e a cada 30 s. Opção "só no Wi-Fi" (depende de o navegador informar o tipo de rede; no iPhone sempre sincroniza). Entrar em outro aparelho recupera tudo.
- **Grupo:** código compartilhado; exige login.

## Limites conhecidos
- Reflexo forte que apaga o texto não é recuperável: o app avisa só pela nitidez; recapture.
- Detecção de bordas é por contraste: funciona melhor com fundo diferente da folha/lousa.
- Imagens são guardadas no Realtime Database (ok para protótipo). Em escala, use Cloud Storage.
- O token de sessão fica no `localStorage`. Em app nativo, use armazenamento seguro (Capacitor).
- Cotas do plano gratuito do Gemini e do Firebase mudam; confira antes de apresentar.

## Mapa do Backlog
HU01 login real (e-mail e Google, recuperação de senha, sessão renovada automaticamente) · HU02 Mais › Organização · HU03/04 grade de aulas + sugestão de Lousa · HU05 perspectiva, luz e nitidez · HU06/07 OCR, PDF/TXT, gatilho de bordas · HU8 pastas/subpastas por conteúdo · HU9 backup e sincronização · HU10 QR seguro · Extra: grupo de estudo.

## App nativo (opcional)
```
npm i @capacitor/core @capacitor/cli && npx cap init CameraAcademica br.fiap.nextcode --web-dir=.
npm i @capacitor/android @capacitor/ios && npx cap add android && npx cap open android
```
