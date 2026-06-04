import os
import sys
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import requests

load_dotenv()

sys.path.append(os.path.dirname(__file__))
from ingest import cargar_documentos, buscar

app = FastAPI()

class Pregunta(BaseModel):
    pregunta: str


@app.on_event("startup")
def startup():
    cargar_documentos(docs_path="docs")


@app.post("/consulta")
def consulta(body: Pregunta):
    pregunta = body.pregunta.strip()

    if not pregunta:
        return {"respuesta": "La pregunta no puede estar vacía."}

    contexto = buscar(pregunta)

    if not contexto:
        return {"respuesta": "No encontré información relacionada en la documentación disponible."}

    contexto_texto = "\n\n".join(contexto)

    prompt = f"""Eres un asistente de soporte técnico. Respondé únicamente basándote en la documentación proporcionada.
Si la información no está en la documentación, indicalo explícitamente. No inventes información.

Documentación relevante:
{contexto_texto}

Pregunta del usuario:
{pregunta}

Respuesta:"""

    try:
        respuesta = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        data = respuesta.json()
        return {"respuesta": data["response"]}
    except Exception as e:
        return {"respuesta": f"Error al consultar el modelo: {str(e)}"}


@app.get("/health")
def health():
    return {"status": "ok"}