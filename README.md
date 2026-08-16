<<<<<<< HEAD
<h1>Humanizy Med</h1>

Humanizy Med é um chatbot inteligente desenvolvido para auxiliar usuários com informações médicas gerais e orientação básica sobre saúde.

### 🎯 Nossa Missão

A Humanizy Med nasceu com o propósito de aproximar a tecnologia da saúde de forma acessível, empática e inteligente.
Nossa missão é oferecer informações médicas confiáveis e suporte rápido para quem busca orientação sobre bem-estar e primeiros cuidados, sempre com o toque humano que a tecnologia deve ter.

> ⚠️ Este projeto **não substitui atendimento médico**. O assistente é orientado, por prompt, a nunca diagnosticar ou prescrever — apenas indicar o tipo de especialista mais adequado.

---

## 🏗️ Estrutura do projeto

O backend é organizado em camadas (rotas → regras de negócio → integrações externas), em vez de um único arquivo:
=======
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
>>>>>>> d4fa4e493555d83f3773026e9a5346df42ab3a76

```
humanizy-med/
├── app/
<<<<<<< HEAD
│   ├── main.py                 # cria a app FastAPI e registra rotas/middlewares
│   ├── config.py               # variáveis de ambiente (validadas no startup)
│   ├── constants.py            # lista de especialistas
│   ├── prompts.py              # prompt de sistema da IA
│   ├── api/routes/             # camada HTTP (chat.py, health.py)
│   ├── schemas/                # contratos de entrada/saída (Pydantic)
│   └── services/                # integrações (Groq, Nominatim)
├── tests/                       # testes automatizados (pytest)
├── docs/ARQUITETURA.md          # decisões de arquitetura e roadmap, em detalhe
└── .github/workflows/ci.yml     # lint + testes no CI
```

Detalhes de cada decisão (por que camadas, por que clientes assíncronos, por que Structured
Outputs em vez de regex etc.) estão em **[docs/ARQUITETURA.md](docs/ARQUITETURA.md)**.

---

## ⚙️ Configuração e execução

### Pré-requisitos
- Python 3.10+
- Uma chave de API do Groq → [console.groq.com/keys](https://console.groq.com/keys)

### Passo a passo

```bash
# 1. Clonar e entrar na pasta
git clone https://github.com/kauavcorreia/chatbot.git
cd chatbot

# 2. Criar e ativar um ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
# edite o .env e preencha GROQ_API_KEY com sua chave real

# 5. Rodar em modo desenvolvimento (recarrega automaticamente)
uvicorn app.main:app --reload
```

A API sobe em `http://localhost:8000`. A documentação interativa (Swagger) fica em
`http://localhost:8000/docs`.

### Variáveis de ambiente

Todas as opções estão documentadas em [`.env.example`](.env.example). As mais relevantes:

| Variável | Obrigatória | Padrão | Descrição |
|---|---|---|---|
| `GROQ_API_KEY` | ✅ | — | Chave de API do Groq. Sem ela a aplicação não sobe. |
| `GROQ_MODEL` | não | `openai/gpt-oss-20b` | Modelo usado na triagem. |
| `CORS_ORIGINS` | não | `http://localhost:3000` | Origens autorizadas a chamar a API, separadas por vírgula. |
| `NOMINATIM_CONTACT_EMAIL` | não | — | Usado no `User-Agent` das chamadas ao Nominatim (exigido pela política de uso deles). |

---

## 📡 Endpoints da API

### `POST /chat`

```json
// Requisição
{
  "message": "Estou com dor de garganta e febre há dois dias",
  "cidade": "Natal"          // opcional — se omitido, "locais" volta vazio
}
```

```json
// Resposta 200
{
  "mensagem": "Pelo que você descreveu, o ideal é procurar um otorrinolaringologista...",
  "especialista": "otorrinolaringologista",
  "emergencia": false,
  "locais": [
    { "nome": "Clínica Exemplo", "lat": "-5.79", "lng": "-35.21", "endereco": "..." }
  ]
}
```

| Código | Quando acontece |
|---|---|
| `200` | Triagem concluída (com ou sem locais, dependendo de `cidade`). |
| `422` | `message` vazio/ausente ou corpo inválido. |
| `502` | Falha ao consultar o serviço de IA. |

### `GET /health`

Retorna `{"status": "ok"}` — usado por monitoramento e orquestradores (Docker/Kubernetes).

---

## 🧪 Testes

```bash
pip install -r requirements-dev.txt
pytest -v
```

Os testes mockam o Groq e o Nominatim (não fazem chamadas reais de rede nem consomem sua
cota de API). O CI (`.github/workflows/ci.yml`) roda lint (`ruff`) e os testes a cada push/PR.

---

## 🐳 Docker

```bash
docker build -t humanizy-med .
docker run -p 8000:8000 --env-file .env humanizy-med
```

---

## 🚀 Tecnologias Utilizadas

O projeto Humanizy Med foi desenvolvido com foco em desempenho, simplicidade e integração com inteligência artificial
As principais tecnologias utilizadas incluem

🐍 Python – linguagem principal do projeto

⚡ FastAPI – framework moderno e rápido para criação de APIs

🧠 Groq API – processamento de linguagem natural e respostas inteligentes (via cliente assíncrono `AsyncGroq`)

🌐 httpx – cliente HTTP assíncrono para a integração com o Nominatim

🔧 pydantic-settings – configuração validada a partir de variáveis de ambiente

🔑 dotenv – gerenciamento de variáveis de ambiente

🚀 Uvicorn – servidor leve e eficiente para rodar a aplicação

🧰 Git e GitHub – versionamento e colaboração do código

🧪 Postman – testes e validação das rotas da API

🎨 HTML, CSS e JavaScript – interface simples e responsiva

---

## 💬 Comunidade e Suporte

Junte-se às nossas discussões da comunidade no GitHub para compartilhar ideias, fazer perguntas ou sugerir melhorias. Vamos construir algo incrível juntos!

[![Abrir Issues](https://img.shields.io/badge/Abrir%20Issues-blue?style=for-the-badge&logo=github)](https://github.com/kauavcorreia/chatbot/issues)

Use o espaço de *issues* para relatar bugs, sugerir melhorias ou tirar dúvidas sobre o projeto 💬

---

## 👥 Contribuidores

Agradecimento especial a todas as pessoas incríveis que contribuíram para este projeto 💙

<a href="https://github.com/kauavcorreia/chatbot/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=kauavcorreia/chatbot" />
</a>

## 📄 Licença

Este projeto é open-source e está disponível sob a Licença MIT. Sinta-se livre para usar, modificar e distribuir para projetos pessoais ou comerciais.

---
<div align="center">
  <p>Feito com ❤️ por <a href="https://github.com/marconi-prog">Marconi Farias</a></p>
</div>
=======
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
>>>>>>> d4fa4e493555d83f3773026e9a5346df42ab3a76
