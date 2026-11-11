# Tienda online: práctica de DevOps

**Autor:** Antón González Formoso

## Descripción

API REST de una tienda online desarrollada en Python con **FastAPI** (Práctica 2). Permite:

- **Usuarios**: registrar clientes (con dirección postal) y administradores, listarlos y consultarlos.
- **Productos**: crear productos genéricos, electrónicos (con meses de garantía) o de ropa (con talla y color), listarlos, consultarlos y eliminarlos.
- **Pedidos**: un cliente realiza un pedido de varios productos. Se comprueba el stock, se descuenta y se calcula el total. Se puede consultar el historial de pedidos de cada cliente.

Los datos se guardan en memoria (no hay base de datos). Al arrancar se crean tres usuarios de ejemplo.

## Estructura

```
.
├── src/
│   ├── main.py                  # Capa de exposición: endpoints de la API (FastAPI)
│   ├── schemas.py               # Esquemas Pydantic de petición y respuesta
│   ├── Services/
│   │   └── Tienda_service.py    # Lógica de negocio (TiendaService) y errores propios
│   └── models/
│       ├── Usuario.py           # Usuario, Cliente, Administrador
│       ├── Producto.py          # Producto, ProductoElectronico, ProductoRopa
│       └── Pedido.py            # Pedido
├── requirements.txt
└── README.md
```

## Ejecución en local (sin Docker)

```bash
pip install -r requirements.txt
uvicorn main:app --app-dir src --reload
```

Abre http://127.0.0.1:8000/docs para probar la API desde Swagger UI.

## Flujo de trabajo con Git

- `main`: rama principal y estable.
- `feature/<nombre>`: una rama corta por cada funcionalidad (por ejemplo, `feature/docker`). Se integra en `main` mediante un Pull Request.
