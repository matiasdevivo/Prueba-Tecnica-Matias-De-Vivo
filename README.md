# Asistente de Soporte Técnico — Prueba Técnica Unilink
**Matías De Vivo**

Sistema de Q&A automatizado que responde preguntas de soporte utilizando documentación técnica interna. Integra n8n como orquestador, Python/FastAPI como backend de recuperación semántica y Ollama (llama3.2) como LLM local.

---

## Arquitectura
Usuario → Webhook (n8n) → HTTP Request → FastAPI (Python) → Ollama (llama3.2)
↑
Búsqueda semántica
sobre /docs

## Stack

- **n8n** — orquestación del workflow via Webhook HTTP
- **Python + FastAPI** — ingesta de documentos, chunking, embeddings y búsqueda semántica
- **Sentence Transformers** — modelo `all-MiniLM-L6-v2` para embeddings
- **Ollama + llama3.2** — LLM local para generación de respuestas
- **scikit-learn** — cosine similarity para recuperación de chunks relevantes

> Se utilizó Ollama como LLM local dado que la API gratuita de OpenAI fue discontinuada. La arquitectura es agnóstica al LLM y puede adaptarse a cualquier proveedor.

---

## Requisitos

- Python 3.9+
- Node.js 18+
- Ollama instalado y corriendo

---

## Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/matiasdevivo/Prueba-Tecnica-Matias-De-Vivo.git
cd Prueba-Tecnica-Matias-De-Vivo
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con las variables necesarias.

### 3. Instalar dependencias Python

```bash
pip3 install fastapi uvicorn sentence-transformers scikit-learn numpy pypdf2 python-dotenv requests
```

### 4. Levantar Ollama con llama3.2

```bash
ollama pull llama3.2
ollama serve
```

### 5. Levantar el servidor Python

```bash
python3 -m uvicorn src.main:app --reload --port 8001
```

### 6. Levantar n8n

```bash
npx n8n
```

Importar el archivo `workflow.json` desde la interfaz de n8n (http://localhost:5678).

### 7. Probar el sistema

```bash
curl -X POST http://localhost:5678/webhook-test/<tu-webhook-id> \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "No puedo iniciar sesión"}'
```

---

## Estructura del proyecto
\```
├── docs/                  # Documentación fuente (.txt, .md, .json, .pdf)
├── src/
│   ├── main.py            # API FastAPI + integración con Ollama
│   └── ingest.py          # Ingesta, chunking, embeddings y búsqueda
├── workflow.json           # Workflow n8n exportado
├── .env.example            # Variables de entorno requeridas
└── README.md
\```
