"""Esquemas Pydantic de la API: validan las peticiones y definen las respuestas"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from models.Pedido import Pedido
from models.Producto import Producto, ProductoElectronico, ProductoRopa
from models.Usuario import Usuario


#Usuarios
class UsuarioCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, examples=["Ana García"])
    email: EmailStr = Field(..., examples=["ana@email.com"])
    tipo: Literal["cliente", "administrador"] = Field(..., examples=["cliente"])
    direccion: Optional[str] = Field(
        default=None, min_length=1, max_length=200, examples=["C/ Real 12, A Coruña"]
    )

    @field_validator("tipo", mode="before")
    @classmethod
    def normalizar_tipo(cls, valor):
        # Acepta "Cliente", " ADMINISTRADOR ", etc.
        return valor.strip().lower() if isinstance(valor, str) else valor

    @model_validator(mode="after")
    def validar_direccion(self):
        if self.tipo == "cliente" and not self.direccion:
            raise ValueError("Un cliente necesita una dirección postal")
        return self


class UsuarioRead(BaseModel):
    id: str
    nombre: str
    email: EmailStr
    es_admin: bool

    @classmethod
    def desde_dominio(cls, usuario: Usuario) -> "UsuarioRead":
        return cls(
            id=usuario.id_usuario,
            nombre=usuario.nombre,
            email=usuario.email,
            es_admin=usuario.is_admin(),
        )


#Producto
TipoProducto = Literal["generico", "electronico", "ropa"]

class ProductoCreate(BaseModel):
    tipo: TipoProducto = Field(..., examples=["electronico"])
    nombre: str = Field(..., min_length=1, max_length=100, examples=["Portátil Lenovo IdeaPad"])
    precio: float = Field(..., ge=0, examples=[649.99])
    stock: int = Field(..., ge=0, examples=[10])
    meses_garantia: Optional[int] = Field(default=None, ge=0, examples=[24])
    talla: Optional[str] = Field(default=None, min_length=1, examples=["M"])
    color: Optional[str] = Field(default=None, min_length=1, examples=["Blanco"])

    @field_validator("tipo", mode="before")
    @classmethod
    def normalizar_tipo(cls, valor):
        return valor.strip().lower() if isinstance(valor, str) else valor

    @model_validator(mode="after")
    def validar_atributos_segun_tipo(self):
        if self.tipo == "electronico":
            if self.meses_garantia is None:
                raise ValueError("Un producto electrónico necesita 'meses_garantia'")
            if self.talla is not None or self.color is not None:
                raise ValueError("Un producto electrónico no admite 'talla' ni 'color'")
        elif self.tipo == "ropa":
            if self.talla is None or self.color is None:
                raise ValueError("Un producto de ropa necesita 'talla' y 'color'")
            if self.meses_garantia is not None:
                raise ValueError("Un producto de ropa no admite 'meses_garantia'")
        else:  # generico
            if (self.meses_garantia is not None or self.talla is not None
                    or self.color is not None):
                raise ValueError(
                    "Un producto genérico no admite 'meses_garantia' ni 'talla' ni 'color'"
                )
        return self


class ProductoRead(BaseModel):
    id: str
    tipo: TipoProducto
    nombre: str
    precio: float
    stock: int
    meses_garantia: Optional[int] = None
    talla: Optional[str] = None
    color: Optional[str] = None

    @classmethod
    def desde_dominio(cls, producto: Producto) -> "ProductoRead":
        datos = dict(
            id=producto.id_producto,
            nombre=producto.nombre,
            precio=producto.precio,
            stock=producto.stock,
        )
        if isinstance(producto, ProductoElectronico):
            return cls(tipo="electronico", meses_garantia=producto.meses_garantia, **datos)
        if isinstance(producto, ProductoRopa):
            return cls(tipo="ropa", talla=producto.talla, color=producto.color, **datos)
        return cls(tipo="generico", **datos)


#Pedido
class PedidoItemCreate(BaseModel):
    producto_id: str = Field(..., min_length=1)
    cantidad: int = Field(..., gt=0, examples=[2])


class PedidoCreate(BaseModel):
    cliente_id: str = Field(..., min_length=1)
    items: list[PedidoItemCreate] = Field(..., min_length=1)


class PedidoItemRead(BaseModel):
    producto_id: str
    nombre: str
    precio_unitario: float
    cantidad: int
    subtotal: float


class PedidoRead(BaseModel):
    id: str
    fecha: datetime
    cliente: UsuarioRead
    total: float
    items: list[PedidoItemRead]

    @classmethod
    def desde_dominio(cls, pedido: Pedido) -> "PedidoRead":
        return cls(
            id=pedido.id_pedido,
            fecha=pedido.fecha,
            cliente=UsuarioRead.desde_dominio(pedido.cliente),
            total=pedido.calcular_total(),
            items=[
                PedidoItemRead(
                    producto_id=producto.id_producto,
                    nombre=producto.nombre,
                    precio_unitario=producto.precio,
                    cantidad=cantidad,
                    subtotal=round(producto.precio * cantidad, 2),
                )
                for producto, cantidad in pedido.items
            ],
        )
