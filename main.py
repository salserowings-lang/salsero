from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import os

app = FastAPI()

# ── CORREGIDO: ahora busca la carpeta llamada "estático" ──
app.mount("/static", StaticFiles(directory="estático"), name="static")

ARCHIVO_DATOS = "datos.json"

def cargar_datos():
    if not os.path.exists(ARCHIVO_DATOS):
        return {
            "productos": [
                {"id": 1, "nombre": "Alitas Clásicas", "precio": 90, "stock": 50, "descripcion": "10 alitas + papas", "imagen": "alitas-clasicas.jpg"},
                {"id": 2, "nombre": "Alitas Picantes", "precio": 100, "stock": 50, "descripcion": "Salsa picante especial", "imagen": "alitas-picantes.jpg"},
                {"id": 3, "nombre": "Alitas BBQ", "precio": 100, "stock": 50, "descripcion": "Salsa barbacoa ahumada", "imagen": "alitas-bbq.jpg"},
                {"id": 4, "nombre": "Alitas Miel Ajo", "precio": 105, "stock": 40, "descripcion": "Dulce y salado", "imagen": "alitas-miel.jpg"},
                {"id": 5, "nombre": "Papas Fritas", "precio": 35, "stock": 100, "descripcion": "Porción grande", "imagen": "papas.jpg"},
                {"id": 6, "nombre": "Refresco 500ml", "precio": 15, "stock": 150, "descripcion": "Coca-Cola / Inca Kola", "imagen": "refresco.jpg"}
            ],
            "pedidos": []
        }
    with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_datos(datos):
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

class ItemPedido(BaseModel):
    producto_id: int
    cantidad: int

class Pedido(BaseModel):
    nombre_cliente: str
    telefono: str
    direccion: str
    ubicacion: Optional[str] = None
    items: List[ItemPedido]

# ── Páginas ──
@app.get("/")
def raiz():
    return FileResponse("estático/index.html")

@app.get("/admin")
def admin():
    return FileResponse("estático/admin.html")

@app.get("/productos")
def productos():
    return FileResponse("estático/productos.html")

@app.get("/pedidos")
def pedidos():
    return FileResponse("estático/pedidos.html")

# ── API Productos ──
@app.get("/api/productos")
def obtener_productos():
    datos = cargar_datos()
    return datos["productos"]

# ── API Pedidos ──
@app.get("/api/pedidos")
def obtener_pedidos():
    datos = cargar_datos()
    return datos["pedidos"]

@app.post("/api/pedidos")
def crear_pedido(pedido: Pedido):
    datos = cargar_datos()
    
    nuevo_pedido = {
        "id": len(datos["pedidos"]) + 1,
        "nombre_cliente": pedido.nombre_cliente,
        "telefono": pedido.telefono,
        "direccion": pedido.direccion,
        "ubicacion": pedido.ubicacion,
        "items": [],
        "total": 0,
        "estado": "pendiente"
    }
    
    total = 0
    for item in pedido.items:
        prod = next((p for p in datos["productos"] if p["id"] == item.producto_id), None)
        if not prod:
            raise HTTPException(status_code=404, detail=f"Producto {item.producto_id} no encontrado")
        if prod["stock"] < item.cantidad:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para {prod['nombre']}")
        
        prod["stock"] -= item.cantidad
        subtotal = prod["precio"] * item.cantidad
        total += subtotal
        nuevo_pedido["items"].append({
            "producto_id": item.producto_id,
            "nombre": prod["nombre"],
            "cantidad": item.cantidad,
            "precio_unitario": prod["precio"],
            "subtotal": subtotal
        })
    
    nuevo_pedido["total"] = total
    datos["pedidos"].insert(0, nuevo_pedido)
    guardar_datos(datos)
    
    return {"mensaje": "Pedido recibido ✅", "pedido": nuevo_pedido}

@app.patch("/api/pedidos/{pedido_id}")
def actualizar_estado(pedido_id: int, estado: str):
    datos = cargar_datos()
    for p in datos["pedidos"]:
        if p["id"] == pedido_id:
            p["estado"] = estado
            guardar_datos(datos)
            return {"mensaje": "Estado actualizado ✅"}
    raise HTTPException(status_code=404, detail="Pedido no encontrado")

@app.get("/api/estado")
def estado_servicio():
    return {"mensaje": "SALSERO funcionando correctamente ✅"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
