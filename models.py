from sqlalchemy import Column, Integer, String


class Mascota():
    __tablename__ = "mascotas" # corregido tablename
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Nombre = Column(String, nullable=False, unique=True)
    Edad = Column(Integer, index=True, autoincrement=True)
    Telefono = Column(Integer, index=True)
    anio_publicacion = Column(String)
    id_vuelo = Column(Integer, Foreign_key=True, index=True, autoincrement=True)
    Tipo = Column(String, nullable=False, unique=True)

class Usuario():
    __tablename__ = "usuarios" # corregido tablename
    id = Column(Integer, Foreign_Key=True, nullable=False)
    Nombre_U = Column(String, nullable=False, unique=True)
    Nombre = Column(Integer, Foreign_Key=True, nullable=False)
    Telefono = Column(Integer, index=True)
    Edad = Column(Integer, index=True)

class Vuelo():
    __tablename__ = "vuelo" # corregido tablename
    id_vuelo = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Aerolinea = Column(String, nullable=False)
    mascotas_id = Column(Integer, Foreign_Key=True, nullable=False)
    fecha = Column(String, nullable=False)
    destino = Column(String, nullable=False)
    origen = Column(String, nullable=False)
    precio= Column(Integer, primary_key=True, index=True, autoincrement=True)

