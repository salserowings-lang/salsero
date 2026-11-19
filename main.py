from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import traceback

app = FastAPI()

# ✅ Ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_DATOS = os.path.join(BASE_DIR, "datos.json")

# ✅ Carpeta SIN tilde: "static"
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ Cargar datos del archivo JSON
def cargar_datos():
    if not os.path.exists(ARCHIVO_DATOS):
        print(f"⚠️ No existe {ARCHIVO_DATOS}, creando por defecto...")
        datos = {
            "productos": [],
            "pedidos": []
        }
        guardar_datos(datos)
        return datos
    
    try:
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error al leer JSON: {e}")
        return {"productos": [], "pedidos": []}

# ✅ Guardar datos en el archivo JSON
def guardar_datos(datos):
    try:
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Error al guardar: {e}")

# ✅ Modelos de datos
class ItemPedido(BaseModel):
    producto_id: int
    cantidad: int

class Pedido(BaseModel):
    nombre_cliente: str
    telefono: str
    direccion: str
    ubicacion: Optional[str] = None
    items: List[ItemPedido]

# ✅ RUTAS DE LAS PÁGINAS
@app.get("/")
def raiz():
    return FileResponse(os.path.join(BASE_DIR, "static", "index.html"))

@app.get("/admin")
def admin_page():
    return FileResponse(os.path.join(BASE_DIR, "static", "admin.html"))

# ✅ API — Productos y Pedidos
@app.get("/api/productos")
def obtener_productos():
    return cargar_datos()["productos"]

@app.get("/api/pedidos")
def obtener_pedidos():
    return cargar_datos()["pedidos"]

@app.post("/api/pedidos")
def crear_pedido(pedido: Pedido):
    try:
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
            subtotal = float(prod["precio"]) * item.cantidad
            total += subtotal
            nuevo_pedido["items"].append({
                "producto_id": item.producto_id,
                "nombre": prod["nombre"],
                "cantidad": item.cantidad,
                "precio_unitario": float(prod["precio"]),
                "subtotal": subtotal
            })
        
        nuevo_pedido["total"] = total
        datos["pedidos"].insert(0, nuevo_pedido)
        guardar_datos(datos)
        
        return {"mensaje": "✅ Pedido recibido", "id": nuevo_pedido["id"]}
    
    except Exception as e:
        print(f"❌ Error al crear pedido: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

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
