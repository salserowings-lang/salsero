
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from typing import List, Optional
import json

app = FastAPI(title="Salsero Wings API")

# ==========================================
# CONFIGURACIÓN DE RUTAS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

# Busca la carpeta static junto a main.py
# o en la carpeta principal del proyecto.
posibles_rutas = [
    BASE_DIR / "static",
    BASE_DIR.parent / "static"
]

STATIC_DIR = next(
    (ruta for ruta in posibles_rutas if ruta.is_dir()),
    BASE_DIR / "static"
)

ARCHIVO_DATOS = BASE_DIR / "datos.json"

# Comprobar que existe la carpeta
if not STATIC_DIR.is_dir():
    raise RuntimeError(
        f"No existe la carpeta static. "
        f"Se esperaba encontrarla en: {STATIC_DIR}"
    )

# Montar archivos estáticos
app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static"
)

# ==========================================
# BASE DE DATOS JSON
# ==========================================

def cargar_datos():

    if not ARCHIVO_DATOS.exists():

        return {
            "productos": [
                {
                    "id": 1,
                    "nombre": "Alitas Clásicas",
                    "precio": 90,
                    "stock": 50,
                    "descripcion": "10 alitas + papas",
                    "imagen": "alitas-clasicas.jpg"
                },
                {
                    "id": 2,
                    "nombre": "Alitas Picantes",
                    "precio": 100,
                    "stock": 50,
                    "descripcion": "Salsa picante especial",
                    "imagen": "alitas-picantes.jpg"
                },
                {
                    "id": 3,
                    "nombre": "Alitas BBQ",
                    "precio": 100,
                    "stock": 50,
                    "descripcion": "Salsa barbacoa ahumada",
                    "imagen": "alitas-bbq.jpg"
                },
                {
                    "id": 4,
                    "nombre": "Alitas Miel Ajo",
                    "precio": 105,
                    "stock": 40,
                    "descripcion": "Dulce y salado",
                    "imagen": "alitas-miel.jpg"
                },
                {
                    "id": 5,
                    "nombre": "Papas Fritas",
                    "precio": 35,
                    "stock": 100,
                    "descripcion": "Porción grande",
                    "imagen": "papas.jpg"
                },
                {
                    "id": 6,
                    "nombre": "Refresco 500ml",
                    "precio": 15,
                    "stock": 150,
                    "descripcion": "Coca-Cola / Inca Kola",
                    "imagen": "refresco.jpg"
                }
            ],
            "pedidos": []
        }

    with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_datos(datos):

    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(
            datos,
            f,
            ensure_ascii=False,
            indent=2
        )


# ==========================================
# MODELOS
# ==========================================

class ItemPedido(BaseModel):
    producto_id: int
    cantidad: int


class Pedido(BaseModel):
    nombre_cliente: str
    telefono: str
    direccion: str
    ubicacion: Optional[str] = None
    items: List[ItemPedido]


# ==========================================
# PÁGINAS WEB
# ==========================================

@app.get("/")
def raiz():

    archivo = STATIC_DIR / "index.html"

    if not archivo.is_file():
        raise HTTPException(
            status_code=404,
            detail="No se encontró index.html"
        )

    return FileResponse(archivo)


@app.get("/admin")
def admin():

    archivo = STATIC_DIR / "admin.html"

    if not archivo.is_file():
        raise HTTPException(
            status_code=404,
            detail="No se encontró admin.html"
        )

    return FileResponse(archivo)


@app.get("/productos")
def productos():

    archivo = STATIC_DIR / "productos.html"

    if not archivo.is_file():
        raise HTTPException(
            status_code=404,
            detail="No se encontró productos.html"
        )

    return FileResponse(archivo)


@app.get("/pedidos")
def pedidos():

    archivo = STATIC_DIR / "pedidos.html"

    if not archivo.is_file():
        raise HTTPException(
            status_code=404,
            detail="No se encontró pedidos.html"
        )

    return FileResponse(archivo)


# ==========================================
# API PRODUCTOS
# ==========================================

@app.get("/api/productos")
def obtener_productos():

    datos = cargar_datos()

    return datos["productos"]


# ==========================================
# API PEDIDOS
# ==========================================

@app.get("/api/pedidos")
def obtener_pedidos():

    datos = cargar_datos()

    return datos["pedidos"]


@app.post("/api/pedidos")
def crear_pedido(pedido: Pedido):

    datos = cargar_datos()

    if not pedido.items:
        raise HTTPException(
            status_code=400,
            detail="El pedido no contiene productos"
        )

    # Validar cantidades
    for item in pedido.items:

        if item.cantidad <= 0:
            raise HTTPException(
                status_code=400,
                detail="La cantidad debe ser mayor que cero"
            )

    # Preparar pedido
    nuevo_pedido = {
        "id": max(
            (p["id"] for p in datos["pedidos"]),
            default=0
        ) + 1,

        "nombre_cliente": pedido.nombre_cliente,
        "telefono": pedido.telefono,
        "direccion": pedido.direccion,
        "ubicacion": pedido.ubicacion,
        "items": [],
        "total": 0,
        "estado": "pendiente"
    }

    total = 0

    # Validar todos los productos antes de modificar stock
    productos_encontrados = []

    for item in pedido.items:

        producto = next(
            (
                p for p in datos["productos"]
                if p["id"] == item.producto_id
            ),
            None
        )

        if producto is None:
            raise HTTPException(
                status_code=404,
                detail=f"Producto {item.producto_id} no encontrado"
            )

        if producto["stock"] < item.cantidad:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para {producto['nombre']}"
            )

        productos_encontrados.append((producto, item))

    # Procesar productos
    for producto, item in productos_encontrados:

        producto["stock"] -= item.cantidad

        subtotal = producto["precio"] * item.cantidad

        total += subtotal

        nuevo_pedido["items"].append({
            "producto_id": item.producto_id,
            "nombre": producto["nombre"],
            "cantidad": item.cantidad,
            "precio_unitario": producto["precio"],
            "subtotal": subtotal
        })

    nuevo_pedido["total"] = total

    datos["pedidos"].insert(0, nuevo_pedido)

    guardar_datos(datos)

    return {
        "mensaje": "Pedido recibido correctamente",
        "pedido": nuevo_pedido
    }


# ==========================================
# ACTUALIZAR ESTADO DEL PEDIDO
# ==========================================

@app.patch("/api/pedidos/{pedido_id}")
def actualizar_estado(pedido_id: int, estado: str):

    estados_validos = [
        "pendiente",
        "preparando",
        "en camino",
        "entregado",
        "cancelado"
    ]

    if estado not in estados_validos:
        raise HTTPException(
            status_code=400,
            detail="Estado no válido"
        )

    datos = cargar_datos()

    for pedido in datos["pedidos"]:

        if pedido["id"] == pedido_id:

            pedido["estado"] = estado

            guardar_datos(datos)

            return {
                "mensaje": "Estado actualizado correctamente"
            }

    raise HTTPException(
        status_code=404,
        detail="Pedido no encontrado"
    )


# ==========================================
# ESTADO DEL SERVICIO
# ==========================================

@app.get("/api/estado")
def estado_servicio():

    return {
        "mensaje": "SALSERO funcionando correctamente"
    }


# ==========================================
# EJECUCIÓN LOCAL
# ==========================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )
