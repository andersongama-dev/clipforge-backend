# ClipForge

ClipForge é uma API desenvolvida em Python com FastAPI para geração automática de clipes a partir de vídeos longos utilizando Inteligência Artificial.

O projeto foi criado com o objetivo de estudar processamento de vídeo, IA generativa e desenvolvimento de APIs, servindo como projeto de aprendizado e portfólio.

> **Aviso:** Este projeto é exclusivamente para fins de estudo e demonstração técnica. Não possui finalidade comercial.

## Tecnologias

* Python 3.12
* FastAPI
* Uvicorn
* OpenRouter
* Llama 3
* Whisper
* FFmpeg
* OpenCV
* MoviePy

## Funcionalidades

* Upload de vídeos.
* Extração automática de áudio.
* Transcrição utilizando Whisper.
* Análise da transcrição com Llama 3 via OpenRouter.
* Identificação automática dos melhores momentos do vídeo.
* Geração automática de clipes utilizando FFmpeg.
* API documentada com Swagger.

## Fluxo de funcionamento

```text
Vídeo
   │
   ▼
Upload
   │
   ▼
Extração de áudio (FFmpeg)
   │
   ▼
Transcrição (Whisper)
   │
   ▼
Análise da IA (Llama 3)
   │
   ▼
Seleção dos melhores trechos
   │
   ▼
Geração dos clipes
```

## Estrutura do projeto

```text
clipforge/
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   └── main.py
│
├── uploads/
├── audios/
├── outputs/
├── prompts/
├── tests/
│
├── requirements.txt
├── .env
└── README.md
```

## Instalação

Clone o repositório:

```bash
git clone <url-do-repositorio>
cd clipforge
```

Crie um ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente virtual.

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
OPENROUTER_API_KEY=sua_chave
MODEL=meta-llama/llama-3.1-8b-instruct
```

## Executando

```bash
uvicorn app.main:app --reload
```

A documentação da API estará disponível em:

```
http://127.0.0.1:8000/docs
```

## Objetivos de aprendizado

Este projeto foi desenvolvido para praticar:

* Arquitetura de APIs com FastAPI.
* Engenharia de prompts.
* Integração com modelos de IA.
* Processamento de áudio e vídeo.
* Manipulação de arquivos.
* Organização de projetos Python.
* Uso do FFmpeg para edição de vídeo.
* Boas práticas de desenvolvimento de software.

## Roadmap

* [x] Upload de vídeos
* [x] Extração de áudio
* [x] Transcrição com Whisper
* [x] Seleção de trechos com IA
* [x] Geração de clipes
* [ ] Legendas automáticas
* [ ] Exportação em formato 9:16
* [ ] Zoom inteligente
* [ ] Detecção de rosto
* [ ] Interface Web
* [ ] Docker
* [ ] Testes automatizados

## Licença

Este projeto está licenciado sob a **MIT License**. Consulte o arquivo [LICENSE](LICENSE) para mais informações.
