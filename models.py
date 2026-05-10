from pydantic import BaseModel
from typing import Optional
from sqlmodel import SQLModel, Field

class Componente(SQLModel):
    nombre: str
    tipo: str
    marca: str
    modelo: str
class ComponenteConId(Componente):
    id: int

class ComponenteActualizado(SQLModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=50)
    tipo: Optional[str] = Field(None, min_length=2, max_length=30)
    marca: Optional[str] = Field(None, min_length=2, max_length=30)
    modelo: Optional[str] = Field(None, min_length=2, max_length=30)
    
class Orden(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    componente_id: int
    componente_nombre: str
    componente_tipo: str
    componente_marca: str
