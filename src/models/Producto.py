#Clases del modelo relacionadas con los productos de la tienda online

import uuid

#Clase base de todos los productos de la tienda cada producto recibe un identificador único generado de forma automática
class Producto:
    def __init__(self, nombre: str, precio: float, stock: int) -> None:
        if precio < 0:
            raise ValueError("El precio no puede ser negativo.")
        if stock < 0:
            raise ValueError("El stock no puede ser negativo.")

        self.id_producto: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.precio: float = precio
        self.stock: int = stock

    #Indica si hay stock suficiente para la cantidad solicitada
    def hay_stock(self, cantidad: int) -> bool:
        return self.stock >= cantidad

    #Actualiza el stock del producto, sumando o restando la cantidad indicada
    def actualizar_stock(self, cantidad: int) -> None:
        if self.stock + cantidad < 0:
            raise ValueError(
                f"Stock insuficiente para '{self.nombre}': "
                f"disponible {self.stock}, se intenta restar {abs(cantidad)}."
            )
        self.stock += cantidad

    #Devuelve las características principales del producto
    def __str__(self) -> str:
        return (
            f"[{self.id_producto[:8]}] {self.nombre} - "
            f"{self.precio:.2f} € - Stock: {self.stock}"
        )

    #Si dos productos son iguales significa que tienen el mismo identificador
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Producto):
            return self.id_producto == other.id_producto
        return False

    def __hash__(self) -> int:
        return hash(self.id_producto)

#Producto electronico con garantia
class ProductoElectronico(Producto):
    def __init__(self, nombre: str, precio: float, stock: int,
                 meses_garantia: int) -> None:
        super().__init__(nombre, precio, stock)
        self.meses_garantia: int = meses_garantia

    #Da la descripción del producto incluyendo la garantía
    def __str__(self) -> str:
        return f"{super().__str__()} - Garantía: {self.meses_garantia} meses"

#Producto de ropa con talla y color
class ProductoRopa(Producto):
    def __init__(self, nombre: str, precio: float, stock: int,
                 talla: str, color: str) -> None:
        super().__init__(nombre, precio, stock)
        self.talla: str = talla
        self.color: str = color

    #Da la descripción del producto incluyendo talla y color
    def __str__(self) -> str:
        return f"{super().__str__()} - Talla: {self.talla} - Color: {self.color}"
