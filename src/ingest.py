import os
import json
import re
from pathlib import Path
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

chunks = []
embeddings = []


def limpiar_texto(texto: str) -> str:
    texto = re.sub(r'\s+', ' ', texto)
    texto = texto.strip()
    return texto


def chunkear(texto: str, tamano: int = 300, overlap: int = 50) -> list[str]:
    palabras = texto.split()
    resultado = []
    i = 0
    while i < len(palabras):
        chunk = " ".join(palabras[i:i + tamano])
        if chunk:
            resultado.append(chunk)
        i += tamano - overlap
    return resultado


def leer_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def leer_md(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def leer_json(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        data = json.load(f)
    return json.dumps(data, ensure_ascii=False, indent=2)


def leer_pdf(path: str) -> str:
    reader = PdfReader(path)
    texto = ""
    for page in reader.pages:
        texto += page.extract_text() or ""
    return texto


def cargar_documentos(docs_path: str = "docs"):
    global chunks, embeddings
    chunks = []

    path = Path(docs_path)
    for archivo in path.iterdir():
        if not archivo.is_file():
            continue

        ext = archivo.suffix.lower()
        try:
            if ext == ".txt":
                texto = leer_txt(str(archivo))
            elif ext == ".md":
                texto = leer_md(str(archivo))
            elif ext == ".json":
                texto = leer_json(str(archivo))
            elif ext == ".pdf":
                texto = leer_pdf(str(archivo))
            else:
                continue

            texto = limpiar_texto(texto)
            nuevos_chunks = chunkear(texto)
            chunks.extend(nuevos_chunks)
            print(f"✓ {archivo.name} — {len(nuevos_chunks)} chunks")

        except Exception as e:
            print(f"✗ Error leyendo {archivo.name}: {e}")

    if chunks:
        print(f"\nGenerando embeddings para {len(chunks)} chunks...")
        embeddings = model.encode(chunks)
        print("✓ Embeddings generados\n")
    else:
        print("⚠ No se encontraron documentos")


def buscar(pregunta: str, top_k: int = 3) -> list[str]:
    if not chunks:
        return []

    query_embedding = model.encode([pregunta])
    similitudes = cosine_similarity(query_embedding, embeddings)[0]
    indices = np.argsort(similitudes)[::-1][:top_k]

    resultados = []
    for i in indices:
        if similitudes[i] > 0.2:
            resultados.append(chunks[i])

    return resultados