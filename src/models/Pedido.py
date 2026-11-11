#Clase del modelo que representa los pedidos de la tienda online

import uuid
from datetime import datetime

from models.Producto import Producto
from models.Usuario import Cliente

#Pedido hecho por un cliente con un lista de productos y cantidades
class Pedido:
    def __init__(self, cliente: Cliente, items: list[tuple[Producto, int]]) -> None:
        self.id_pedido: str = str(uuid.uuid4())
        self.cliente: Cliente = cliente
        self.items: list[tuple[Producto, int]] = list(items)
        self.fecha: datetime = datetime.now()

    #Hace el calculo del precio total
    def calcular_total(self) -> float:
        total = sum(producto.precio * cantidad for producto, cantidad in self.items)
        return round(total, 2)

    #Devuelve un resumen del pedido del cliente incluyendo el precio total
    def __str__(self) -> str:
        lineas = [
            f"  - {cantidad} x {producto.nombre} "
            f"({producto.precio:.2f} € c/u) = {producto.precio * cantidad:.2f} €"
            for producto, cantidad in self.items
        ]
        return "\n".join(
            [
                f"Pedido {self.id_pedido[:8]} - {self.fecha:%d/%m/%Y %H:%M:%S}",
                f"Cliente: {self.cliente.nombre}",
                *lineas,
                f"Total: {self.calcular_total():.2f} €",
            ]
        )
