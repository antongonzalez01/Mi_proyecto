#Clases del modelo relacionadas con los usuarios de la tienda online

import uuid

#Representa a cualquier persona que interactúa con la tienda cada usuario recibe un identificador único generado de forma automática
class Usuario:

    def __init__(self, nombre: str, email: str) -> None:
        self.id_usuario: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.email: str = email
    #Indica si el usuario es administrador o no
    def is_admin(self) -> bool:
        return False

    def __str__(self) -> str:
        return f"[{self.id_usuario[:8]}] {self.nombre} <{self.email}>"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Usuario):
            return self.id_usuario == other.id_usuario
        return False

    def __hash__(self) -> int:
        return hash(self.id_usuario)


class Cliente(Usuario):
    def __init__(self, nombre: str, email: str, direccion: str) -> None:
        """Crea un cliente.
        Argumentoss:
            nombre: nombre del cliente.
            email: correo electrónico del cliente.
            direccion: dirección postal del cliente.
        """
        super().__init__(nombre, email)
        self.direccion: str = direccion
    #Devuelve la descripción del cliente incluyendo su direccion
    def __str__(self) -> str:
        return f"Cliente {super().__str__()} - Dirección: {self.direccion}"


class Administrador(Usuario):
    #Si el usuario es administrador siempre devuelve True
    def is_admin(self) -> bool:
        return True

    def __str__(self) -> str:
        return f"Administrador {super().__str__()}"
