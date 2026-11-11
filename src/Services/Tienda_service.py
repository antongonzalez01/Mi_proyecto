"""Gestiona de forma centralizada las operaciones de la tienda."""

from typing import Optional

from models.Pedido import Pedido
from models.Producto import Producto, ProductoElectronico, ProductoRopa
from models.Usuario import Administrador, Cliente, Usuario


# Excepciones propias de la tienda.
# Heredan de ValueError para que el código de la Práctica 1 siga funcionando igual,
# pero permiten a la API distinguir el tipo de error y devolver el código HTTP adecuado.
class TiendaError(ValueError):
    """Error genérico de negocio (petición incorrecta) -> 400."""


class NoEncontradoError(TiendaError):
    """El usuario o producto solicitado no existe -> 404."""


class ConflictoError(TiendaError):
    """La operación choca con el estado actual (email duplicado, stock...) -> 409."""


class TiendaService:
    """Intermediario entre los usuarios y los productos de la tienda.

    Mantiene en memoria los usuarios registrados, el inventario de productos
    y el histórico de pedidos.
    """

    def __init__(self) -> None:
        self.usuarios: dict[str, Usuario] = {}
        self.productos: dict[str, Producto] = {}
        self.pedidos: list[Pedido] = []

    #Usuarios
    def registrar_usuario(self, tipo: str, nombre: str, email: str,
                          direccion: Optional[str] = None) -> Usuario:
        """Registra un nuevo usuario en la tienda.

        Argumentos:
            tipo: "cliente" o "administrador"
            nombre: nombre del usuario
            email: correo electrónico (debe ser único en la tienda)
            direccion: dirección postal (obligatoria para los clientes)
        """
        if any(usuario.email == email for usuario in self.usuarios.values()):
            raise ConflictoError(f"Ya existe un usuario con el email '{email}'.")

        tipo_normalizado = tipo.strip().lower()
        if tipo_normalizado == "cliente":
            if not direccion:
                raise TiendaError("Un cliente necesita una direccion")
            usuario: Usuario = Cliente(nombre, email, direccion)
        elif tipo_normalizado == "administrador":
            usuario = Administrador(nombre, email)
        else:
            raise TiendaError(
                f"Tipo de usuario no válido: '{tipo}' "
                "(usar solo'cliente' o 'administrador')."
            )

        self.usuarios[usuario.id_usuario] = usuario
        return usuario

    #Devuelve un usuario a partir de su identificador
    def obtener_usuario(self, id_usuario: str) -> Usuario:
        usuario = self.usuarios.get(id_usuario)
        if usuario is None:
            raise NoEncontradoError(f"El usuario con id '{id_usuario}' no existe.")
        return usuario

    #Devuelve todos los usuarios registrados
    def ver_usuarios(self) -> list[Usuario]:
        return list(self.usuarios.values())

    #Productos
    #Crea un producto del tipo indicado (genérico, electrónico o ropa) y lo añade al inventario
    def crear_producto(self, tipo: str, nombre: str, precio: float, stock: int,
                       meses_garantia: Optional[int] = None,
                       talla: Optional[str] = None,
                       color: Optional[str] = None) -> Producto:
        tipo_normalizado = tipo.strip().lower()
        try:
            if tipo_normalizado == "generico":
                producto: Producto = Producto(nombre, precio, stock)
            elif tipo_normalizado == "electronico":
                if meses_garantia is None:
                    raise TiendaError("Un producto electrónico necesita 'meses_garantia'")
                producto = ProductoElectronico(nombre, precio, stock, meses_garantia)
            elif tipo_normalizado == "ropa":
                if not talla or not color:
                    raise TiendaError("Un producto de ropa necesita 'talla' y 'color'")
                producto = ProductoRopa(nombre, precio, stock, talla, color)
            else:
                raise TiendaError(
                    f"Tipo de producto no válido: '{tipo}' "
                    "(usar solo uno de los siguientes: 'generico', 'electronico' o 'ropa')."
                )
        except TiendaError:
            raise
        except ValueError as error:  # validaciones del modelo (precio/stock negativos)
            raise TiendaError(str(error)) from error

        self.agregar_producto(producto)
        return producto

    #Añade un producto al inventario
    def agregar_producto(self, producto: Producto) -> None:
        self.productos[producto.id_producto] = producto

    #Devuelve un producto a partir de su identificador
    def obtener_producto(self, id_producto: str) -> Producto:
        producto = self.productos.get(id_producto)
        if producto is None:
            raise NoEncontradoError(f"El producto con id '{id_producto}' no existe.")
        return producto

    #Elimina un producto del inventario a partir de su identificador
    def borrar_producto(self, id_producto: str) -> bool:
        return self.productos.pop(id_producto, None) is not None

    #Devuelve todos los productos disponibles en la tienda
    def ver_productos(self) -> list[Producto]:
        return list(self.productos.values())

    #Pedidos
    #Crea un pedido si el usuario existe y hay stock suficiente de los productos que haya pedido
    def realizar_pedido(self, id_usuario: str,
                        items: list[tuple[str, int]]) -> Pedido:
        usuario = self.obtener_usuario(id_usuario)
        if not isinstance(usuario, Cliente):
            raise TiendaError("Solo los clientes pueden realizar pedidos")
        if not items:
            raise TiendaError("El pedido no contiene ningún producto")

        # Agrupamos las cantidades por producto por si un mismo id se repite
        cantidades: dict[str, int] = {}
        for id_producto, cantidad in items:
            if cantidad <= 0:
                raise TiendaError("Las cantidades deben ser mayor a cero")
            cantidades[id_producto] = cantidades.get(id_producto, 0) + cantidad

        # Validamos existencia y stock de todos los productos antes de descontar
        lineas: list[tuple[Producto, int]] = []
        for id_producto, cantidad in cantidades.items():
            producto = self.obtener_producto(id_producto)
            if not producto.hay_stock(cantidad):
                raise ConflictoError(
                    f"Stock insuficiente de '{producto.nombre}': "
                    f"solicitadas {cantidad}, disponibles {producto.stock}."
                )
            lineas.append((producto, cantidad))

        # Todo correcto: descontamos el stock y creamos el pedido
        for producto, cantidad in lineas:
            producto.actualizar_stock(-cantidad)

        pedido = Pedido(usuario, lineas)
        self.pedidos.append(pedido)
        return pedido

    #Devuelve los pedidos de un usuario ordenados por fecha (el más antiguo primero)
    def ver_pedidos_usuario(self, id_usuario: str) -> list[Pedido]:
        self.obtener_usuario(id_usuario)  # lanza NoEncontradoError si no existe

        pedidos_usuario = [
            pedido for pedido in self.pedidos
            if pedido.cliente.id_usuario == id_usuario
        ]
        return sorted(pedidos_usuario, key=lambda pedido: pedido.fecha)
