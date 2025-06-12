from typing import Dict, List, Optional, Tuple, Any
from models import Mascota, Vuelo, Usuario
from datetime import datetime
import json
import os


class MascotaError(Exception):
    """Custom exception for transaction-related errors"""
    pass


class sigmotoaFlights:
    def __init__(self):
        self.mascotas: Dict[int, Mascota] = {}
        self.vuelos: Dict[Tuple[int, str], Vuelo] = {}  # Key: (item_id, date)
        self.usuarios: Dict[str, Usuario] = {}
        self.item_images: Dict[str, str] = {}  # Key: item_id (str), Value: image_filename (str)

        # Auto-incrementing IDs
        self._next_mascota_id = 1
        # _next_market_item_id será inicializado en startup_event basado en datos existentes
        # _next_usuario_id_counter es para un posible auto-generador de IDs de jugador (no usado actualmente en forms)
        self._next_usuario_id_counter = 1

        # --- Helper for ID generation ---

    def _get_next_mascota_id(self) -> int:
        """Generates the next available transaction ID."""
        current_id = self._next_mascota_id
        self._next_mascota_id += 1
        return current_id

    def _get_next_vuelo_id(self) -> int:
        """Generates the next available market item ID based on existing items."""
        if not self.vuelos:
            return 1
        # Extraer todos los id_vuelo de las claves (vuelo_id, date)
        max_id = max(id_vuelo for id_vuelo, _ in self.vuelos.keys())
        return max_id + 1

    # --- Mascotas ---
    def add_mascota(self, mascota: Mascota) -> None:
        if mascota.id <= 0:
            mascota.id = self._get_next_mascota_id()
        elif mascota.id in self.mascotas:
            raise ValueError(f"Mascota ID {mascota.id} already exists")

        Usuario = self.usuarios.get(mascota.usuario_id)
        if not Usuario:
            raise MascotaError(f"Usuario {mascota.player_id} not found")

    def get_mascota(self, id: int) -> Optional[Mascota]:
        """Get a transaction by its ID."""
        return self.mascotas.get(id)

    def get_usuarios_mascotas(self, player_id: str) -> List[Mascota]:
        """Get all mascotas for a specific player."""
        return [t for t in self.mascotas.values() if t.player_id == player_id]

    def update_mascota(self, id: int, id_vuelo: int) -> None:
        """Update an existing mascota's amount."""
        mascota = self.mascotas.get(id)
        if not mascota:
            raise MascotaError(f"Mascota {id} not found")
        # Note: A real system would need more complex logic for balance adjustments on update
        mascota.id_vuelo = id_vuelo

    def delete_mascota(self, id: int) -> None:
        """Delete a mascota and revert usuario balance/total_spent."""
        mascota = self.mascotas.get(id)
        if not mascota:
            raise MascotaError(f"Mascota {id} not found")
        del self.mascotas[id]

    # --- Market Prices (Items) ---
    def add_vuelo(self, vuelo: Vuelo) -> None:
        """Add a new vuelo."""
        key = (vuelo.id_vuelo, vuelo.fecha)
        if key in self.vuelos:
            # You might want to update instead of raising an error here, depending on desired behavior
            raise ValueError(f"Vuelo {vuelo.item_id} on {vuelo.date} already exists.")
        self.vuelos[key] = vuelo

    def get_vuelo(self, id_vuelo: int, fecha: str) -> Optional[Vuelo]:
        """Get a market precio for a specific item on a specific date."""
        return self.vuelos.get((id_vuelo, fecha))

    def get_all_vuelos(self) -> List[Vuelo]:
        """Get all recorded market prices."""
        return list(self.vuelos.values())

    def update_vuelo(self, id_vuelo: int, fecha: str, new_price: Optional[int] = None,
                            New_Aerolinea: Optional[str] = None) -> None:
        """Update an existing vuelo entry."""
        key = (id_vuelo, fecha)
        vuelo = self.vuelos.get(key)
        if not vuelo:
            raise ValueError(f"Vuelo {id_vuelo} on {fecha} not found.")
        if new_price is not None:
            vuelo.precio = new_price
        if New_Aerolinea is not None:
            vuelo.Aerolinea = New_Aerolinea
        # Note: If item_id or date needs to change, it's effectively a delete + add.

    def delete_vuelo(self, id_vuelo: int, fecha: str) -> None:
        """Delete a specific vuelo entry."""
        key = (id_vuelo, fecha)
        if key not in self.vuelos:
            raise ValueError(f"Vuelo {id_vuelo} on {fecha} not found.")
        del self.vuelos[key]

    # --- Players ---
    def add_usuario(self, usuario: Usuario) -> None:
        """Add a new player."""
        if usuario.player_id in self.usuarios:
            raise ValueError(f"Usuario ID {usuario.player_id} already exists.")
        self.usuarios[usuario.player_id] = usuario

    def get_usuario(self, player_id: str) -> Optional[Usuario]:
        """Get a player by their ID."""
        return self.usuarios.get(player_id)

    def update_usuario_info(self, player_id: str, Nombre_U: Optional[str] = None) -> None:
        """Update a usuario's username."""
        usuario = self.usuarios.get(player_id)
        if not usuario:
            raise ValueError(f"Usuario {player_id} not found")
        if Nombre_U is not None:
            usuario.username = Nombre_U

    def delete_usuario(self, player_id: str) -> None:
        """Delete a Usuario and all their associated mascotas."""
        if player_id not in self.usuarios:
            raise ValueError(f"Usuario {player_id} not found")

        # Eliminar transacciones asociadas a este jugador
        mascotas_to_delete = [
            trans_id for trans_id, trans_obj in self.mascotas.items()
            if trans_obj.player_id == player_id
        ]
        for trans_id in mascotas_to_delete:
            del self.mascotas[trans_id]

        del self.usuarios[player_id]