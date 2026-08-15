# Humanizy-Med-2.0

# Arquitetura — Humanizy Med

Este documento explica como o backend está organizado, por que cada decisão foi tomada e o
que fica como próximo passo. Ele complementa o [README.md](../README.md), que foca em "como
rodar"; aqui o foco é "como funciona e por quê".

## Visão geral

O `Main.py` original concentrava em um único arquivo: configuração, prompt, chamada à IA,
chamada de geolocalização e a rota HTTP. Funcionava, mas qualquer mudança (trocar de provedor
de IA, adicionar um teste, adicionar uma segunda rota) exigia mexer no mesmo arquivo que faz
tudo. A reestruturação separa isso em camadas com responsabilidade única:

```
humanizy-med/
├── app/
│   ├── main.py              # monta a app FastAPI e registra middlewares/rotas
│   ├── config.py            # Settings (variáveis de ambiente), validado no startup
│   ├── constants.py         # lista de especialistas (fonte única de verdade)
│   ├── prompts.py           # prompt de sistema da IA
│   ├── api/routes/          # camada HTTP — só recebe/valida request e devolve response
│   │   ├── chat.py          # POST /chat
│   │   └── health.py        # GET /health
│   ├── schemas/              # contratos de entrada/saída (Pydantic)
│   │   └── chat.py
│   └── services/              # regras de negócio e integrações externas
│       ├── ai_service.py     # Groq (triagem estruturada)
│       └── location_service.py  # Nominatim (busca de locais)
├── tests/                    # testes automatizados (pytest), com as integrações mockadas
├── docs/ARQUITETURA.md       # este arquivo
├── .github/workflows/ci.yml  # lint + testes a cada push/PR
├── Dockerfile
├── requirements.txt          # dependências de produção
└── requirements-dev.txt      # + pytest, ruff (não vai para produção)
```

A regra prática: **rotas não sabem como o Groq ou o Nominatim funcionam** — elas só chamam
`ai_service.gerar_resposta(...)` ou `location_service.buscar_especialistas(...)` e traduzem o
resultado (ou o erro) em uma resposta HTTP. Isso significa que trocar de provedor de IA no
futuro, por exemplo, é uma mudança isolada em `ai_service.py`.

## Fluxo de uma requisição `POST /chat`

1. FastAPI valida o corpo da requisição contra `ChatRequest` (schema). Mensagem vazia já é
   rejeitada aqui com `422`, antes de gastar uma chamada à IA.
2. `api/routes/chat.py` chama `ai_service.gerar_resposta(mensagem)`.
3. `ai_service` chama o Groq pedindo uma resposta em **Structured Outputs / modo estrito**: o
   modelo é obrigado (por decodificação restrita) a devolver um JSON com `mensagem`,
   `especialista` (dentro de um enum fechado) e `emergencia`. Não há mais "adivinhação" por
   busca de texto.
4. Se a cidade foi informada, `location_service.buscar_especialistas(...)` consulta o
   Nominatim (com cache) para aquele especialista + cidade.
5. A rota monta o `ChatResponse` final. Se a IA falhar, a requisição inteira falha (`502`) —
   sem triagem não há o que responder. Se **só** a geolocalização falhar, a triagem ainda é
   devolvida normalmente, com `locais: []` (degradação graciosa: um provedor externo instável
   não deveria derrubar a funcionalidade principal).

## Por que Structured Outputs em vez de buscar palavras na resposta

O código original pedia texto livre para a IA e depois procurava, por substring, qual
especialista da lista aparecia na resposta:

```python
tipo_encontrado = next((e for e in especialistas if e in resposta_texto.lower()), "clínico geral")
```

Isso tem um bug sutil: a busca percorre a lista `ESPECIALISTAS` **na ordem em que ela foi
declarada**, não na ordem em que os termos aparecem no texto da IA. Um texto como *"não é
cardiologista, e sim dermatologista"* seria classificado como `cardiologista`, porque essa
palavra aparece primeiro na lista interna — mesmo que o especialista certo, segundo o próprio
texto, seja outro. Também é sensível a acentuação e pode confundir substrings.

A troca para `response_format` com `json_schema` + `strict: true` (suportado pelos modelos
`openai/gpt-oss-20b`/`120b` no Groq) resolve isso na raiz: o `especialista` é restrito por um
`enum` no schema, então a própria IA só pode retornar um dos valores válidos — não há mais
parsing de texto livre para o especialista. De brinde, isso também permitiu adicionar o campo
`emergencia` (booleano) de forma confiável, algo que seria ainda mais frágil de extrair de um
texto livre.

Referência: <https://console.groq.com/docs/structured-outputs>

## Decisões de arquitetura (resumo)

| Decisão | Por quê |
|---|---|
| `AsyncGroq` + `httpx.AsyncClient` em vez de `Groq` + `requests` | O `Main.py` original chamava bibliotecas **síncronas** dentro de uma rota `async def`. Isso bloqueia o event loop do FastAPI: enquanto uma requisição espera o Groq ou o Nominatim responder, o processo inteiro fica preso e não atende mais ninguém. Com clientes assíncronos, o servidor continua atendendo outras requisições nesse meio-tempo. |
| `pydantic-settings` com `groq_api_key: str` obrigatório | *Fail fast*: se a variável de ambiente não existir, a aplicação recusa subir, com um erro claro. Antes, o erro só apareceria (de forma confusa) na primeira mensagem de um usuário real. |
| Erros tratados em cada service (`AIServiceError`, `LocationServiceError`) | O código original não tinha nenhum `try/except` ao redor das chamadas externas — qualquer instabilidade de rede vira um `500` genérico para o usuário. Agora cada falha vira uma exceção de domínio, tratada explicitamente na rota. |
| Cache em memória no `location_service` | O Nominatim é um serviço público mantido por doações, com política de uso restrita a **1 requisição/segundo** e que exige cache do lado do cliente. Ver <https://operations.osmfoundation.org/policies/nominatim/>. |
| Validação de entrada no schema (`min_length`, strip) | Deixa o FastAPI devolver `422` automaticamente para entradas inválidas, em vez de checar `if not mensagem.strip()` manualmente dentro da rota e devolver `200` com uma mensagem de erro dentro do corpo. |

## O que muda para quem já usava o `Main.py`

| Antes (`Main.py`) | Agora |
|---|---|
| `Groq(...)` síncrono | `AsyncGroq(...)` em `app/services/ai_service.py` |
| `requests.get(...)` síncrono | `httpx.AsyncClient` em `app/services/location_service.py` |
| Prompt inline no `Main.py` | `app/prompts.py` |
| Lista `especialistas` inline | `app/constants.py` |
| Tudo em uma função `chat()` | `api/routes/chat.py` (HTTP) chamando `services/` (regra de negócio) |
| Sem testes | `tests/` com Groq e Nominatim mockados (não bate na rede) |
| `model="llama-3.1-8b-instant"` | `model="openai/gpt-oss-20b"` (ver seção abaixo) |

## ⚠️ Migração de modelo urgente

O modelo usado no `Main.py` original, `llama-3.1-8b-instant`, está na
[página de descontinuações do Groq](https://console.groq.com/docs/deprecations) com
**desligamento em 16/08/2026** — ou seja, chamadas a esse `model=` param passam a devolver
erro a partir dessa data. O substituto recomendado oficialmente pelo Groq é
`openai/gpt-oss-20b`, que já é o padrão configurado em `app/config.py`. Se você clonar este
projeto depois dessa data, não precisa fazer nada; se for aplicar só parte dessas mudanças no
seu `Main.py` atual, troque o `model=` primeiro — é a mudança de maior urgência aqui.

## Roadmap sugerido (por prioridade)

### Já aplicado nesta reestruturação
- Clientes assíncronos ponta a ponta (Groq e Nominatim)
- Migração para `openai/gpt-oss-20b` + Structured Outputs
- Configuração *fail-fast* com `pydantic-settings`
- Tratamento de erro com degradação graciosa
- Cache simples para o Nominatim
- Testes automatizados + CI (lint e testes a cada PR)
- `Dockerfile` para empacotar a aplicação

### Curto prazo (baixo esforço, alto impacto)
- Restringir `CORS_ORIGINS` para os domínios reais do frontend em produção (hoje o padrão é
  só `localhost`, o que já é mais seguro que `["*"]`, mas precisa ser configurado por
  ambiente).
- Rate limiting no `/chat` (ex.: [`slowapi`](https://github.com/laurentS/slowapi)) para
  evitar abuso e custo inesperado de API.
- Logging estruturado (ex.: `structlog`) em vez de `print`/logging básico.

### Médio prazo
- Histórico de conversa: hoje cada mensagem é tratada isoladamente; um chat "de verdade"
  normalmente mantém contexto entre turnos (exigiria persistir sessão/histórico).
- Autenticação por API key para consumidores da API (se o frontend não for o único cliente).
- Observabilidade: métricas de latência/erro por dependência externa (Groq, Nominatim).
- Avaliar a [LGPD](https://www.gov.br/anpd) para o fluxo: mensagens sobre sintomas são dado
  pessoal sensível (art. 5º, II), o que impõe requisitos de tratamento, retenção e consentimento.
  Isso é uma constatação, não uma opinião jurídica — vale revisão com quem cuida da parte legal
  do projeto.

### Longo prazo / infraestrutura
- Cache compartilhado (Redis) em vez de cache em memória por processo, necessário assim que
  a aplicação rodar com mais de um worker/instância.
- Avaliar um provedor de geocodificação pago (Google Places, LocationIQ, Geoapify) se o volume
  de uso crescer além do que a política gratuita do Nominatim comporta.

## Referências

- Groq — Structured Outputs: <https://console.groq.com/docs/structured-outputs>
- Groq — Descontinuação de modelos: <https://console.groq.com/docs/deprecations>
- Groq — SDK Python (`AsyncGroq`): <https://github.com/groq/groq-python>
- Nominatim — Política de uso: <https://operations.osmfoundation.org/policies/nominatim/>
- FastAPI — Documentação oficial: <https://fastapi.tiangolo.com/>
