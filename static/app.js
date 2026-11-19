// ===== CONFIGURACIÓN =====
const API = "/api";
let productos = [];
let carrito = [];

// ===== INICIO =====
document.addEventListener("DOMContentLoaded", function() {
    console.log("✅ Página cargada");
    cargarProductos();
});

// ===== CARGAR PRODUCTOS =====
async function cargarProductos() {
    console.log("🔄 Cargando productos...");
    try {
        const respuesta = await fetch(`${API}/productos`);
        
        if (!respuesta.ok) {
            throw new Error(`Error del servidor: ${respuesta.status}`);
        }
        
        productos = await respuesta.json();
        console.log("✅ Productos recibidos:", productos);
        mostrarProductos();
        
    } catch (error) {
        console.error("❌ Error:", error);
        const contenedor = document.getElementById("lista-productos");
        if (contenedor) {
            contenedor.innerHTML = '<p style="color:red;text-align:center;padding:20px;">Error al cargar productos</p>';
        }
    }
}

// ===== MOSTRAR PRODUCTOS =====
function mostrarProductos() {
    const contenedor = document.getElementById("lista-productos");
    if (!contenedor) {
        console.error("❌ No se encontró el contenedor #lista-productos");
        return;
    }
    
    contenedor.innerHTML = "";
    
    if (!productos || productos.length === 0) {
        contenedor.innerHTML = '<p style="text-align:center;color:#777;padding:20px;">No hay productos disponibles</p>';
        return;
    }
    
    productos.forEach(function(p) {
        const precio = parseFloat(p.precio || 0);
        const tarjeta = document.createElement("div");
        tarjeta.className = "tarjeta";
        tarjeta.innerHTML = `
            <h3>${p.nombre}</h3>
            <p>${p.descripcion || ''}</p>
            <p class="precio">Bs ${precio.toFixed(2)}</p>
            <button onclick="agregarAlCarrito(${p.id})">➕ Agregar</button>
        `;
        contenedor.appendChild(tarjeta);
    });
}

// ===== CARRITO BÁSICO =====
function agregarAlCarrito(id) {
    const producto = productos.find(function(p) { return p.id === id; });
    if (!producto) return;
    
    carrito.push({
        id: id,
        nombre: producto.nombre,
        precio: parseFloat(producto.precio || 0),
        cantidad: 1
    });
    
    alert(`✅ "${producto.nombre}" agregado al carrito`);
    console.log("🛒 Carrito:", carrito);
}

