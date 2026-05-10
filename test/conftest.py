import sys
from pathlib import Path

# --- Añadir raíz del proyecto al PYTHONPATH ---
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import os
import pandas as pd
import pytest
from starlette.testclient import TestClient

# Importar la factoría que crea la app igual que main.py
from app.factory import create_app


@pytest.fixture(scope="function")
def tmp_project_dir(tmp_path, monkeypatch):
    """
    Cambia el cwd a un directorio temporal para evitar modificar archivos reales.
    """
    p = tmp_path

    # Crear estructura mínima
    (p / "templates").mkdir()
    (p / "static").mkdir()

    # Cambiar cwd para que las rutas relativas de CSV apunten aquí
    monkeypatch.chdir(p)

    yield p
    # pytest borra automáticamente tmp_path


@pytest.fixture(scope="function")
def client(tmp_project_dir):
    """
    Crea el TestClient utilizando la app creada por create_app(),
    asegurando que incluye estáticos, templates, middleware y routers.
    También genera los CSV mínimos necesarios para las pruebas.
    """

    # Crear archivos CSV mínimos
    pd.DataFrame(columns=["id", "nombre_usuario", "correo", "contraseña_hash"]).to_csv("usuarios.csv", index=False)

    componentes = pd.DataFrame([
        {"id": 1, "nombre": "MB-1", "tipo": "Motherboard", "socket": "AM4", "tipo_ram": "DDR4", "marca": "MSI", "modelo": "MB-1"},
        {"id": 2, "nombre": "CPU-AM4-1", "tipo": "CPU", "socket": "AM4", "tipo_ram": "", "marca": "AMD", "modelo": "Ryzen"},
        {"id": 3, "nombre": "RAM-DDR4-8GB", "tipo": "RAM", "socket": "", "tipo_ram": "DDR4", "marca": "Corsair", "modelo": "8GB"},
        {"id": 4, "nombre": "GPU-1", "tipo": "GPU", "socket": "", "tipo_ram": "", "marca": "NVIDIA", "modelo": "GTX"},
        {"id": 5, "nombre": "HDD-1", "tipo": "HDD", "socket": "", "tipo_ram": "", "marca": "Seagate", "modelo": "HDD1"},

        # Incompatibles
        {"id": 6, "nombre": "CPU-INT", "tipo": "CPU", "socket": "LGA1200", "tipo_ram": "", "marca": "Intel", "modelo": "i5"},
        {"id": 7, "nombre": "RAM-DDR3", "tipo": "RAM", "socket": "", "tipo_ram": "DDR3", "marca": "Kingston", "modelo": "4GB"}
    ])
    componentes.to_csv("componentes.csv", index=False)

    pd.DataFrame(columns=["correo_usuario", "orden", "id", "nombre", "tipo", "marca", "modelo"]).to_csv("orden.csv", index=False)
    pd.DataFrame(columns=["orden", "id", "nombre", "tipo", "marca", "modelo"]).to_csv("eliminados.csv", index=False)

    #    # Crear la app EXACTAMENTE igual que main.py
    app = create_app()

    # Crear cliente de pruebas SIN seguir redirecciones
    client = TestClient(app, follow_redirects=False)

    yield client
