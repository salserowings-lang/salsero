from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json
from datetime import datetime
from typing import List, Optional

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Modelos
class ItemPedido(BaseModel):
    id: int
    cantidad: int

class Pedido(BaseModel):
    id: Optional[int] = None
    nombre: str
    ci_nit: str
    telefono: str
    direccion: str
    ubicacion_gps: Optional[str] = ""
    items: List[ItemPedido]
    fecha: Optional[str] = None
    estado: Optional[str] = "pendiente"

# Rutas de páginas
@app.get("/")
async def raiz():
    return FileResponse("static/index.html")

@app.get("/admin.html")
async def admin():
    return FileResponse("static/admin.html")

@app.get("/lista-productos")
async def lista_productos():
    return FileResponse("static/productos.html")

@app.get("/lista-pedidos")
async def lista_pedidos():
    return FileResponse("static/pedidos.html")

# API — Obtener productos
@app.get("/productos")
def obtener_productos():
    with open("datos.json", "r", encoding="utf-8") as f:
        datos = json.load(f)
    return datos.get("productos", [])

# API — Obtener todos los pedidos
@app.get("/pedidos")
def obtener_pedidos():
    with open("datos.json", "r", encoding="utf-8") as f:
        datos = json.load(f)
    return datos.get("pedidos", [])

# API — Crear nuevo pedido
@app.post("/pedidos")
def crear_pedido(pedido: Pedido):
    with open("datos.json", "r+", encoding="utf-8") as f:
        datos = json.load(f)
        if "pedidos" not in datos:
            datos["pedidos"] = []
        nuevo_id = len(datos["pedidos"]) + 1
        pedido.id = nuevo_id
        pedido.fecha = datetime.now().isoformat()
        pedido.estado = "pendiente"
        datos["pedidos"].append(pedido.dict())
        f.seek(0)
        f.truncate()
        json.dump(datos, f, indent=2, ensure_ascii=False)
    return {"mensaje": "Pedido recibido correctamente", "id": nuevo_id}

# API — Eliminar pedido por ID
@app.delete("/pedidos/{pedido_id}")
def eliminar_pedido(pedido_id: int):
    with open("datos.json", "r+", encoding="utf-8") as f:
        datos = json.load(f)
        if "pedidos" not in datos:
            raise HTTPException(status_code=404, detail="No hay pedidos")
        
        lista_pedidos = datos["pedidos"]
        indice = next((i for i, p in enumerate(lista_pedidos) if p.get("id") == pedido_id), None)
        
        if indice is None:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        eliminado = lista_pedidos.pop(indice)
        f.seek(0)
        f.truncate()
        json.dump(datos, f, indent=2, ensure_ascii=False)
    
    return {"mensaje": "Pedido eliminado correctamente", "pedido": eliminado}


