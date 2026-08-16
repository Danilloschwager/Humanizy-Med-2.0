<h1>Humanizy Med</h1>

Humanizy Med é um chatbot inteligente desenvolvido para auxiliar usuários com informações médicas gerais e orientação básica sobre saúde.

### 🎯 Nossa Missão

A Humanizy Med nasceu com o propósito de aproximar a tecnologia da saúde de forma acessível, empática e inteligente.
Nossa missão é oferecer informações médicas confiáveis e suporte rápido para quem busca orientação sobre bem-estar e primeiros cuidados, sempre com o toque humano que a tecnologia deve ter.

> ⚠️ Este projeto **não substitui atendimento médico**. O assistente é orientado, por prompt, a nunca diagnosticar ou prescrever — apenas indicar o tipo de especialista mais adequado.

---

## 🏗️ Estrutura do projeto

O backend é organizado em camadas (rotas → regras de negócio → integrações externas), em vez de um único arquivo:

```
humanizy-med/
├── app/
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
