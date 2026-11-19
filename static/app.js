const API = "/api";
let productos = [];
let carrito = [];
let coordenadas = { lat: null, lng: null };
let categoriaActiva = "Todos";

document.addEventListener("DOMContentLoaded", cargarProductos);

async function cargarProductos() {
    try {
        const res = await fetch(`${API}/productos`);
        if (!res.ok) throw new Error("Error en la respuesta");
        productos = await res.json();
        console.log("✅ Productos cargados:", productos);
        mostrarProductos();
    } catch (error) {
        console.error("❌ Error:", error);
        alert("❌ No se pudo cargar los productos. Intenta de nuevo.");
    }
}

function mostrarProductos() {
    const contenedor = document.getElementById("lista-productos");
    if (!contenedor) return;
    
    contenedor.innerHTML = "";

    const filtrados = categoriaActiva === "Todos" 
        ? productos 
        : productos.filter(p => p.categoria === categoriaActiva);

    if (!filtrados || filtrados.length === 0) {
        contenedor.innerHTML = "<p style='grid-column:1/-1;text-align:center;color:#777;'>No hay productos disponibles</p>";
        return;
    }

    filtrados.forEach(p => {
        const precio = parseFloat(p.precio || 0);
        const stock = parseInt(p.stock || 10);
        const sinStock = stock <= 0;
        
        contenedor.innerHTML += `
            <div class="tarjeta ${sinStock ? 'sin-stock' : ''}">
                <img src="static/${p.imagen || ''}" alt="${p.nombre}" onerror="this.src='https://via.placeholder.com/300x160?text=SALSERO'">
                <div class="info">
                    <h3>${p.nombre}</h3>
                    <p>${p.descripcion || ''}</p>
                    <p class="precio">Bs ${precio.toFixed(2)}</p>
                    <p class="stock">${stock > 0 ? `✅ Disponible` : '❌ Agotado'}</p>
                    <button class="btn-agregar" onclick="agregarAlCarrito(${p.id})" ${sinStock ? 'disabled' : ''}>
                        ${sinStock ? 'Agotado' : '➕ Agregar'}
                    </button>
                </div>
            </div>
        `;
    });
}

function filtrar(categoria) {
    categoriaActiva = categoria;
    document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('activo'));
    if (event && event.target) event.target.classList.add('activo');
    mostrarProductos();
}

function agregarAlCarrito(id) {
    const producto = productos.find(p => p.id === id);
    if (!producto) return;
    
    const precio = parseFloat(producto.precio || 0);
    const stock = parseInt(producto.stock || 10);
    
    if (stock <= 0) return;

    const existente = carrito.find(item => item.producto_id === id);
    if (existente) {
        if (existente.cantidad < stock) existente.cantidad++;
        else { alert(`Solo hay ${stock} unidades disponibles`); return; }
    } else {
        carrito.push({
            producto_id: id,
            nombre: producto.nombre,
            cantidad: 1,
            precio_unitario: precio
        });
    }
    actualizarCarrito();
}

function actualizarCarrito() {
    const contador = document.getElementById("contador");
    const total = carrito.reduce((sum, i) => sum + (parseFloat(i.precio_unitario) * i.cantidad), 0);
    const items = document.getElementById("lista-carrito");

    const totalItems = carrito.reduce((s, i) => s + i.cantidad, 0);
    if (contador) contador.textContent = totalItems;

    if (carrito.length === 0) {
        if (items) items.innerHTML = "<p class='vacio'>Tu carrito está vacío</p>";
        const totalElem = document.getElementById("total");
        if (totalElem) totalElem.textContent = "Total: Bs 0.00";
        return;
    }

    if (items) {
        items.innerHTML = "";
        carrito.forEach((item, index) => {
            const subtotal = parseFloat(item.precio_unitario) * item.cantidad;
            items.innerHTML += `
                <div class="item-carrito">
                    <div>
                        <strong>${item.nombre}</strong><br>
                        Bs ${parseFloat(item.precio_unitario).toFixed(2)} c/u
                    </div>
                    <div class="cantidad">
                        <button onclick="cambiarCantidad(${index}, -1)">−</button>
                        <span>${item.cantidad}</span>
                        <button onclick="cambiarCantidad(${index}, 1)">+</button>
                    </div>
                </div>
            `;
        });
    }
    const totalElem = document.getElementById("total");
    if (totalElem) totalElem.textContent = `Total: Bs ${total.toFixed(2)}`;
}

function cambiarCantidad(index, cambio) {
    const item = carrito[index];
    const producto = productos.find(p => p.id === item.producto_id);
    const stock = producto ? parseInt(producto.stock || 10) : 999;
    
    item.cantidad += cambio;
    if (item.cantidad <= 0) carrito.splice(index, 1);
    else if (item.cantidad > stock) {
        alert(`Solo hay ${stock} unidades disponibles`);
        item.cantidad = stock;
    }
    actualizarCarrito();
}

function abrirCarrito() {
    const modal = document.getElementById("modal-carrito");
    if (modal) modal.classList.add("activo");
    actualizarCarrito();
}

function cerrarCarrito() {
    const modal = document.getElementById("modal-carrito");
    if (modal) modal.classList.remove("activo");
}

function obtenerUbicacion() {
    const estado = document.getElementById("estado-ubicacion");
    if (!estado) return;
    
    if (!navigator.geolocation) {
        estado.innerHTML = "❌ Tu navegador no soporta ubicación";
        return;
    }
    estado.innerHTML = "⏳ Obteniendo ubicación...";
    navigator.geolocation.getCurrentPosition(
        (pos) => {
            coordenadas.lat = pos.coords.latitude;
            coordenadas.lng = pos.coords.longitude;
            estado.innerHTML = `✅ Ubicación capturada: ${coordenadas.lat.toFixed(5)}, ${coordenadas.lng.toFixed(5)}`;
        },
        (err) => {
            estado.innerHTML = "❌ Error: " + err.message;
        }
    );
}

async function enviarPedido() {
    if (carrito.length === 0) { alert("Agrega productos al carrito"); return; }

    const nombre = document.getElementById("nombre-cliente")?.value.trim();
    const telefono = document.getElementById("telefono")?.value.trim();
    const direccion = document.getElementById("direccion")?.value.trim();
    const referencia = document.getElementById("referencia")?.value.trim() || "";

    if (!nombre || !telefono || !direccion) { alert("Completa todos los datos de entrega"); return; }

    const items = carrito.map(i => ({
        producto_id: i.producto_id,
        cantidad: i.cantidad
    }));

    const pedido = {
        nombre_cliente: nombre,
        telefono: telefono,
        direccion: direccion,
        ubicacion: referencia + (coordenadas.lat ? ` (${coordenadas.lat}, ${coordenadas.lng})` : ""),
        items: items
    };

    try {
        const res = await fetch(`${API}/pedidos`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(pedido)
        });

        if (!res.ok) throw await res.json();

        alert("✅ ¡Pedido enviado correctamente! Gracias por tu compra");
        carrito = [];
        cerrarCarrito();
        cargarProductos();

        document.getElementById("nombre-cliente").value = "";
        document.getElementById("telefono").value = "";
        document.getElementById("direccion").value = "";
        document.getElementById("referencia").value = "";
        const estado = document.getElementById("estado-ubicacion");
        if (estado) estado.innerHTML = "";
        coordenadas = { lat: null, lng: null };

    } catch (error) {
        alert("❌ Error: " + (error.detail || "No se pudo enviar el pedido"));
    }
}
