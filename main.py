from fastapi import FastAPI, HTTPException, Depends, Query, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Union,List, Dict, Any, Type, TypeVar, Callable, Optional, Tuple  # Asegúrate que Tuple y Any estén aquí
from datetime import datetime
import csv
import os
import json
import shutil
from contextlib import asynccontextmanager
import random
import uvicorn  # Solo para referencia, no es necesario para ejecutar
import base64  # Utilizado en algún punto para imágenes, si no se usa puede eliminarse
import traceback  # Importado para ver el traceback completo en la consola
import matplotlib.pyplot as plt  # Importa matplotlib
import io                       # Para manejar datos en memoria
import base64                   # Para codificar imágenes a base64


from pkg_resources import iter_entry_points

from models import Mascota,Usuario,Vuelo
from operations import  sigmotoaFlights, MascotaError

app=FastAPI()

# --- Data File Paths ---
DATA_DIR = "data"
MASCOTAS_FILE = os.path.join(DATA_DIR, "Mascotas.csv")
USUARIOS_FILE = os.path.join(DATA_DIR, "Usuarios.csv")
VUELOS_FILE = os.path.join(DATA_DIR, "Vuelos.csv")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def load_Mascotas(ops: 'sigmotoaFlights'):
    print(f"DEBUG: Intentando cargar mascotas desde: {MASCOTAS_FILE}")
    if not os.path.exists(MASCOTAS_FILE):
        print(f"DEBUG: ¡ERROR! Archivo de mascotas NO ENCONTRADO en: {MASCOTAS_FILE}")
        return
    try:
        with open(MASCOTAS_FILE, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            print(f"DEBUG: Cabeceras del archivo Mascotas.csv: {reader.fieldnames}")
            rows_read = 0
            for row in reader:
                try:
                    Id = int(row['Id'])
                    Nombre = row['Nombre']
                    Edad = row['Edad']
                    Telefono = int(row['Telefono'])
                    Años = row['Años']
                    id_vuelo = row['Id_vuelo']
                    Tipo=row['Tipo']
                    mascota = Mascota(
                        Id=Id,
                        Nombre=Nombre,
                        Edad=Edad,
                        Telefono=Telefono,
                        Años=Años,
                        Tipo=Tipo,

                    )
                    ops.mascotas[id] = mascota
                    ops._next_mascota_id = max(ops._next_mascota_id, id + 1)
                    rows_read += 1
                except (ValueError, KeyError) as e:
                    print(f"DEBUG: ERROR al leer fila de mascotas: {row} - {e}")
            print(f"DEBUG: Se leyeron {rows_read} filas de Mascotas.csv")
    except Exception as e:
        print(f"DEBUG: ERROR general al abrir/leer Mascotas.csv: {e}")

def save_mascotas(mascotas: Dict[int, Mascota]):
    if not mascotas:
        # If no transactions, ensure file is empty or just create header
        with open(MASCOTAS_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Id', 'Nombre', 'Edad', 'Telefono', 'Años', 'Tipo'])
        return

    with open(MASCOTAS_FILE, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ['id', 'Nombre', 'Edad', 'Telefono', 'Años', 'Tipo']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for mascota in mascotas.values():
            writer.writerow({
                'id': mascota.id,
                'Nombre': mascota.Nombre,
                'Edad': mascota.Edad,
                'Telefono': mascota.Telefono,
                'Años': mascota.anio_publicacion,
                'Tipo': mascota.Tipo
            })


def load_vuelos(ops: 'GTAOnlineOperations'):
    print(f"DEBUG: Intentando cargar vuelos: {VUELOS_FILE}")
    if not os.path.exists(VUELOS_FILE):
        print(f"DEBUG: ¡ERROR! Archivo de vuelos NO ENCONTRADO en: {VUELOS_FILE}")
        return
    try:
        with open(VUELOS_FILE, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            print(f"DEBUG: Cabeceras del archivo Vuelos.csv: {reader.fieldnames}")
            rows_read = 0
            for row in reader:
                try:
                    id_vuelo = int(row['id_vuelo'])
                    Aerolinea = row['Aerolinea']
                    precio = int(row['precio'])
                    fecha = row['fecha']
                    vuelo = Vuelo(id_vuelo=id_vuelo, Aerolinea=Aerolinea, precio=precio, fecha=fecha)
                    ops.vuelos[(id_vuelo, fecha)] = vuelo
                    rows_read += 1
                except (ValueError, KeyError) as e:
                    print(f"DEBUG: ERROR al leer fila de vuelos: {row} - {e}")
            print(f"DEBUG: Se leyeron {rows_read} filas de Vuelos.csv")
    except Exception as e:
        print(f"DEBUG: ERROR general al abrir/leer Vuelos.csv: {e}")


def save_vuelos(vuelos: Dict[Tuple[int, str], Vuelo]):
    if not vuelos:
        with open(VUELOS_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['id_vuelo', 'Aerolinea', 'precio', 'fecha'])
        return

    with open(VUELOS_FILE, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ['id_vuelo', 'Aerolinea', 'precio', 'fecha']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for vuelo in vuelos.values():
            writer.writerow({
                'id_vuelo': vuelo.id_vuelo,
                'Aerolinea': vuelo.Aerolinea,
                'precio': vuelo.precio,
                'fecha': vuelo.fecha
            })


def load_usuarios(ops: 'sigmotoaFlights'):
    print(f"DEBUG: Intentando cargar usuarios desde: {USUARIOS_FILE}")
    if not os.path.exists(USUARIOS_FILE):
        print(f"DEBUG: ¡ERROR! Archivo de Usuarios NO ENCONTRADO en: {USUARIOS_FILE}")
        return
    try:
        with open(USUARIOS_FILE, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            print(f"DEBUG: Cabeceras del archivo Usuarios.csv: {reader.fieldnames}")
            rows_read = 0
            for row in reader:
                try:
                    player_id = row['player_id']
                    Nombre_U = row['Nombre_U']
                    Telefono = row['Telefono']
                    Edad = row['Edad']
                    usuario = Usuario(
                        player_id=player_id,
                        Nombre_U=Nombre_U,
                        Telefono=Telefono,
                        Edad=Edad
                    )
                    ops.usuarios[player_id] = usuario
                    rows_read += 1
                except (ValueError, KeyError) as e:
                    print(f"DEBUG: ERROR al leer fila de usuario: {row} - {e}")
            print(f"DEBUG: Se leyeron {rows_read} filas de Usuarios.csv")
    except Exception as e:
        print(f"DEBUG: ERROR general al abrir/leer Usuarios.csv: {e}")


def save_usuarios(usuarios: Dict[str, Usuario]):
    if not usuarios:
        with open(USUARIOS_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['player_id', 'Nombre_U', 'Telefono', 'Edad'])
        return

    with open(USUARIOS_FILE, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ['player_id', 'Nombre_U', 'Telefono', 'Edad']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for Usuario in usuarios.values():
            writer.writerow({
                'player_id': Usuario.id,
                'Nombre_U': Usuario.Nombre_U,
                'Telefono': Usuario.Telefono,
                'Edad': Usuario.Edad
            })




# --- Initialize GTAOnlineOperations ---
ops = sigmotoaFlights()
# --- FastAPI App Initialization ---
app = FastAPI(
    title="SigmotoaFlishts",
    description="Bienvenido a sigmotoa dev, una empresa con presencia en varios paises, con nosotros la prioridad es su mascota.",
    version="2.0.0",
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

# --- App Lifespan (Load/Save Data) ---
@app.on_event("startup")
async def startup_event():
    global ops
    print("DEBUG: Iniciando evento de startup...")
    print(f"DEBUG: Después de cargar datos. Número de Mascotas: {len(ops.mascotas)}")
    print(f"DEBUG: Después de cargar datos. Número de Usuarios: {len(ops.usuarios)}")
    print(f"DEBUG: Después de cargar datos. Número de Vuelos: {len(ops.vuelos)}")

@app.on_event("shutdown")
async def shutdown_event():
    print("Guardando datos al cerrar la aplicación...")
    save_mascotas(ops.mascotas)
    save_vuelos(ops.vuelos)
    save_usuarios(ops.usuarios)
    print("Datos guardados. Aplicación apagada.")

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/Mascotas/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

if __name__ == "__main__":
    # Obtener el puerto del entorno (Render lo proporciona) o usar 8000 como predeterminado
    port = int(os.environ.get("PORT", 8000))
    # Iniciar el servidor uvicorn, vinculándolo a 0.0.0.0 para aceptar conexiones externasAdd commentMore actions
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)