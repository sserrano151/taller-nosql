"""
API REST - Taller: Integración NoSQL con FastAPI y MongoDB
==========================================================
Tecnologías: FastAPI + PyMongo + MongoDB
Despliegue: Render
Consumo: Oracle APEX
"""

from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError



app = FastAPI(
    title="API Bares - Taller NoSQL",
    description="API REST conectada a MongoDB para gestión de bares, comentarios y eventos.",
    version="1.0.0"
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


MONGO_URI = os.environ.get("MONGO_URI", "")
DB_NAME = os.environ.get("DB_NAME", "")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    db = client[DB_NAME]
    print(f" Conectado a MongoDB - Base de datos: '{DB_NAME}'")
except ConnectionFailure as e:
    print(f" Error de conexión a MongoDB: {e}")
    db = None


def get_collection(name: str):
    if db is None:
        raise HTTPException(
            status_code=503,
            detail="Base de datos no disponible. Verifica la variable MONGO_URI."
        )
    return db[name]




@app.get("/")
def inicio():
    return {
        "estado": "API funcionando correctamente",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }



@app.get("/bares/{bar_id}/comentarios")
def get_comentarios(bar_id: int):
    col = get_collection("comentarios_bares")
    try:
        docs = list(col.find({"bar_id": bar_id}))
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar comentarios: {str(e)}")


@app.post("/bares/{bar_id}/comentarios")
def post_comentario(bar_id: int, datos: dict):
    col = get_collection("comentarios_bares")
    if "texto" not in datos or not datos["texto"].strip():
        raise HTTPException(
            status_code=422,
            detail="El campo 'texto' es obligatorio y no puede estar vacío."
        )
    datos["bar_id"] = bar_id
    datos["fecha"] = datetime.now().isoformat()
    try:
        resultado = col.insert_one(datos)
        return {
            "mensaje": "Comentario guardado exitosamente",
            "id": str(resultado.inserted_id)
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar comentario: {str(e)}")


@app.get("/bares/{bar_id}/eventos")
def get_eventos(bar_id: int):
    col = get_collection("eventos")
    try:
        docs = list(col.find({"bar_id": bar_id}))
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar eventos: {str(e)}")


@app.post("/bares/{bar_id}/eventos")
def post_evento(bar_id: int, datos: dict):
    col = get_collection("eventos")
    if "nombre" not in datos or not datos["nombre"].strip():
        raise HTTPException(
            status_code=422,
            detail="El campo 'nombre' es obligatorio y no puede estar vacío."
        )
    datos["bar_id"] = bar_id
    datos["fecha_creacion"] = datetime.now().isoformat()
    try:
        resultado = col.insert_one(datos)
        return {
            "mensaje": "Evento creado exitosamente",
            "id": str(resultado.inserted_id)
        }
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar evento: {str(e)}")