from typing import Union
from fastapi import FastAPI
import os
import uvicorn

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

if __name__ == "__main__":
    # Obtener el puerto del entorno (Render lo proporciona) o usar 8000 como predeterminado
    port = int(os.environ.get("PORT", 8000))
    # Iniciar el servidor uvicorn, vinculándolo a 0.0.0.0 para aceptar conexiones externasAdd commentMore actions
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)