from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import *
from datetime import datetime
from typing import List, Optional
import bcrypt
import os
import pandas as pd

USERS_CSV = "usuarios.csv"
ORDEN_CSV = "orden.csv"

async def crear_componente(comp: Componente, session: AsyncSession) -> Componente:
    session.add(comp)
    await session.commit()
    await session.refresh(comp)
    return comp

async def obtener_componentes(session: AsyncSession) -> List[Componente]:
    result = await session.exec(select(Componente))
    return result.all()

async def obtener_componente(id: int, session: AsyncSession) -> Optional[Componente]:
    return await session.get(Componente, id)

async def buscar_componente(tipo: str, modelo: str, session: AsyncSession) -> Optional[Componente]:
    result = await session.exec(select(Componente).where(Componente.tipo == tipo, Componente.modelo == modelo))
    return result.first()

async def actualizar_componente(id: int, datos: ComponenteActualizado, session: AsyncSession) -> Optional[Componente]:
    componente = await session.get(Componente, id)
    if not componente:
        return None
    for k, v in datos.dict(exclude_unset=True).items():
        setattr(componente, k, v)
    componente.fecha_modificacion = datetime.utcnow()
    session.add(componente)
    await session.commit()
    await session.refresh(componente)
    return componente

async def eliminar_componente(id: int, session: AsyncSession) -> Optional[Componente]:
    comp = await session.get(Componente, id)
    if not comp:
        return None
    await session.delete(comp)
    await session.commit()
    return comp

#---------------------LOGIN---------------------------------------

def hash_password(plain_password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False
    
def ensure_users_csv_exists():
    if not os.path.exists(USERS_CSV):
        df = pd.DataFrame(columns=["id","nombre_usuario","correo","contraseña_hash"])
        df.to_csv(USERS_CSV, index=False)

def get_user_by_username(correo: str):
    ensure_users_csv_exists()
    df = pd.read_csv(USERS_CSV)
    row = df[df["correo"] == correo]
    if row.empty:
        return None
    return row.iloc[0].to_dict()

def create_user(nombre_usuario: str, correo: str, plain_password: str):
    ensure_users_csv_exists()
    df = pd.read_csv(USERS_CSV)
    if (df["correo"] == correo).any():
        raise ValueError("Ya existe una cuenta asociada a este correo")
    next_id = int(df["id"].max()) + 1 if not df.empty else 1
    hashed = hash_password(plain_password)
    df_new = pd.DataFrame([{"id": next_id, "nombre_usuario": nombre_usuario, "correo": correo, "contraseña_hash": hashed}])
    df = pd.concat([df, df_new], ignore_index=True)
    df.to_csv(USERS_CSV, index=False)
    return next_id

def update_user_password(correo: str, new_plain_password: str):
    ensure_users_csv_exists()
    df = pd.read_csv(USERS_CSV)
    idx = df[df["correo"] == correo].index
    if idx.empty:
        raise ValueError("Usuario no encontrado")
    df.loc[idx, "contraseña_hash"] = hash_password(new_plain_password)
    df.to_csv(USERS_CSV, index=False)
    return True



"""
async def crear_distribuidor(distri: Distribuidores, session: AsyncSession) -> Distribuidores:
    session.add(distri)
    await session.commit()
    await session.refresh(distri)
    return distri

async def obtener_distribuidores(session: AsyncSession) -> List[Distribuidores]:
    result = await session.exec(select(Distribuidores))
    return result.all()

async def obtener_distribuidor(id: int, session: AsyncSession) -> Optional[Distribuidores]:
    return await session.get(Distribuidores, id)

async def buscar_distribuidor(nombre: str, session: AsyncSession) -> Optional[Distribuidores]:
    result = await session.exec(select(Distribuidores).where(Distribuidores.nombre == nombre))
    return result.first()

async def actualizar_distribuidor(id: int, datos: DistriActualizado, session: AsyncSession) -> Optional[Distribuidores]:
    distribuidor = await session.get(Distribuidores, id)
    if not distribuidor:
        return None
    for k, v in datos.dict(exclude_unset=True).items():
        setattr(distribuidor, k, v)
    session.add(distribuidor)
    await session.commit()
    await session.refresh(distribuidor)
    return distribuidor

async def eliminar_distribuidor(id: int, session: AsyncSession) -> Optional[Distribuidores]:
    dist = await session.get(Distribuidores, id)
    if not dist:
        return None
    await session.delete(dist)
    await session.commit()
    return dist
"""