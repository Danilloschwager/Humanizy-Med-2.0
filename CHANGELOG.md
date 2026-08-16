# Changelog — Refatoração de arquitetura (v0.1 → v0.2)

Este documento resume a atualização feita em cima do `Main.py` original: por que ela existe,
o que mudou de fato no código, e o que ainda fica como próximo passo. Pensado para colar na
descrição de um Pull Request ou numa release do GitHub.

## TL;DR

O projeto inteiro estava em um único arquivo (`Main.py`), sem testes, com chamadas de rede
síncronas dentro de rotas assíncronas, sem tratamento de erro, e usando um modelo do Groq que
**é descontinuado em 16/08/2026**. Esta atualização reorganiza o código em camadas
(rotas → regras de negócio → integrações), corrige os bugs de concorrência/parsing, adiciona
testes automatizados + CI, e migra para o modelo recomendado pelo Groq.

Nenhum comportamento de produto muda para quem consome a API — o contrato de `POST /chat`
continua o mesmo, só ganhou o campo `emergencia` a mais na resposta.

---

## ⚠️ Breaking / ação necessária

- **`GROQ_API_KEY` agora é obrigatória no startup.** Se ela não estiver definida, a aplicação
  recusa subir (antes, o erro só aparecia — de forma confusa — na primeira mensagem de um
  usuário real). Configure via `.env` (veja `.env.example`).
- **Modelo trocado**: `llama-3.1-8b-instant` → `openai/gpt-oss-20b`. O modelo antigo está
  na [página de descontinuações do Groq](https://console.groq.com/docs/deprecations) com
  desligamento em 16/08/2026; o novo é o substituto oficialmente recomendado.
- **`requests` saiu, `httpx` entrou** nas dependências (`requirements.txt`).
- Nova dependência: **`pydantic-settings`**, para validar as variáveis de ambiente.

## 🗂️ Reorganização de arquivos

O `Main.py` (arquivo único) foi dividido em módulos por responsabilidade:

| Antes | Depois |
|---|---|
| Tudo em `Main.py` | `app/main.py` (monta a app) |
| Config inline (`load_dotenv()` + `os.getenv`) | `app/config.py` (`pydantic-settings`, validado no startup) |
| Lista `especialistas` inline | `app/constants.py` |
| Prompt inline | `app/prompts.py` |
| `ChatRequest` inline | `app/schemas/chat.py` (+ `ChatResponse`, `Local`) |
| Chamada ao Groq dentro da rota | `app/services/ai_service.py` |
| `buscar_especialistas()` dentro do `Main.py` | `app/services/location_service.py` |
| Rota `/chat` | `app/api/routes/chat.py` |
| _(não existia)_ | `app/api/routes/health.py` (`GET /health`) |
| _(não existia)_ | `tests/` (13 testes, Groq e Nominatim mockados) |
| _(não existia)_ | `.github/workflows/ci.yml` (lint + testes no CI) |
| _(não existia)_ | `Dockerfile` |
| _(não existia)_ | `docs/ARQUITETURA.md` (decisões de design em detalhe) |

## 🐛 Bugs corrigidos

1. **Chamadas de rede síncronas em rota assíncrona.** `Groq(...)` e `requests.get(...)`
   bloqueavam o event loop do FastAPI — enquanto uma requisição esperava resposta do Groq ou
   do Nominatim, o processo inteiro ficava travado para todo mundo. Trocado por `AsyncGroq` e
   `httpx.AsyncClient`.

2. **Especialista escolhido por ordem errada.** O código original buscava, por substring, qual
   especialista da lista `ESPECIALISTAS` aparecia na resposta da IA — mas percorria a lista na
   ordem em que ela foi *declarada*, não na ordem em que os termos apareciam no *texto*. Um
   texto como "não é cardiologista, e sim dermatologista" virava `cardiologista`, porque essa
   palavra vinha primeiro na lista interna. Resolvido eliminando o parsing de texto: agora a
   IA retorna o especialista já estruturado (Structured Outputs do Groq, com `enum` fechado),
   então essa ambiguidade não existe mais.

3. **Nenhum tratamento de erro nas chamadas externas.** Qualquer instabilidade do Groq ou do
   Nominatim virava um `500` genérico. Agora cada serviço tem sua própria exceção
   (`AIServiceError`, `LocationServiceError`), tratada explicitamente na rota — e uma falha só
   no Nominatim não derruba a triagem principal (a resposta volta normalmente, com
   `locais: []`).

4. **Nenhum timeout nas chamadas HTTP.** Uma chamada travada no Groq ou no Nominatim podia
   prender a requisição indefinidamente. Agora ambos têm timeout configurável
   (`GROQ_TIMEOUT_SECONDS`, `NOMINATIM_TIMEOUT_SECONDS`).

5. **`User-Agent` com e-mail de exemplo** (`seu_email_real@gmail.com`) nas chamadas ao
   Nominatim — a política deles exige um identificador real; deixado como placeholder no
   original. Agora vem de `NOMINATIM_CONTACT_EMAIL`.

## ✨ Melhorias adicionadas

- **Structured Outputs em modo estrito** para a resposta da IA — elimina o parsing de texto
  livre e adiciona um campo `emergencia` (booleano) confiável, que a resposta original não
  tinha.
- **Cache em memória** para consultas ao Nominatim (mesma cidade + especialidade não bate na
  rede de novo dentro do TTL configurado) — a política de uso deles pede isso explicitamente.
- **Validação de entrada no schema** (`ChatRequest`): mensagem vazia agora retorna `422`
  automaticamente, em vez de um `200` com texto de erro no corpo.
- **`GET /health`** para monitoramento/orquestração (Docker, Kubernetes, uptime checks).
- **CORS configurável** por variável de ambiente, em vez de `allow_origins=["*"]` fixo.
- **13 testes automatizados** cobrindo triagem, emergência, cache, erros de rede e o
  endpoint `/chat` de ponta a ponta — todos mockados, não consomem cota de API nem fazem
  chamadas reais de rede.
- **CI no GitHub Actions**: lint (`ruff`) + testes a cada push/PR.
- **`Dockerfile`** com usuário não-root e imagem `slim`.

## 📄 Contrato da API — o que mudou

`POST /chat` continua recebendo o mesmo corpo (`message`, `cidade` opcional). A única mudança
na resposta é um campo novo:

```diff
 {
   "mensagem": "...",
   "especialista": "cardiologista",
+  "emergencia": false,
   "locais": [...]
 }
```

## Próximos passos (não incluídos nesta atualização)

Ficaram documentados em detalhe no roadmap do `docs/ARQUITETURA.md`: rate limiting no `/chat`,
histórico de conversa entre turnos, autenticação por API key, observabilidade, cache
compartilhado (Redis) para múltiplos workers, e uma revisão de LGPD (mensagens sobre sintomas
são dado pessoal sensível).
