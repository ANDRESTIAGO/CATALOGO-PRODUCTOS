from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()
DATA_CSV = "data.csv"

def load_data():
    try:
        # Usar encoding latin-1 o utf-8-sig por si hay caracteres especiales ocultos
        df = pd.read_csv(DATA_CSV, encoding='utf-8')
        
        # Normalizar nombres de columnas (quitar espacios y acentos para evitar KeyErrors)
        df.columns = [c.strip() for c in df.columns]
        
        # Mapear nombres según lo encontrado en el archivo (Division sin acento)
        # Asegurar que las columnas existan antes de operar
        col_map = {
            'División': 'Division',
            'Género': 'Genero'
        }
        for target, actual in col_map.items():
            if actual in df.columns and target not in df.columns:
                df[target] = df[actual]

        # Llenar nulos
        df['Division'] = df['Division'].fillna('Sin Categoría').astype(str)
        df['Genero'] = df['Genero'].fillna('Unisex').astype(str)
        df['Deporte'] = df['Deporte'].fillna('General').astype(str)
        df['nombre'] = df['nombre'].fillna('Sin Nombre').astype(str)
        
        return df
    except FileNotFoundError:
        return pd.DataFrame()

@router.get("/", response_class=HTMLResponse)
async def ver_catalogo(request: Request):
    df = load_data()
    if df.empty:
        return templates.TemplateResponse(request, "home.html", {"productos": [], "mensaje": "No hay productos disponibles."})
    
    # Agrupar por Referencia para la vista principal
    productos = df.drop_duplicates(subset=['Referencia']).to_dict(orient="records")
    
    # Obtener filtros únicos usando los nombres reales del CSV
    filtros = {
        "categorias": sorted([str(x) for x in df["Division"].unique()]),
        "generos": sorted([str(x) for x in df["Genero"].unique()]),
        "deportes": sorted([str(x) for x in df["Deporte"].unique()])
    }
    
    return templates.TemplateResponse(request, "home.html", {
        "productos": productos,
        "filtros": filtros
    })

@router.get("/buscar", response_class=HTMLResponse)
async def buscar_productos(
    request: Request, 
    q: str = "", 
    categoria: str = "", 
    genero: str = "", 
    deporte: str = ""
):
    df_all = load_data()
    df = df_all.copy()
    
    if q:
        df = df[df['nombre'].str.contains(q, case=False) | df['Referencia'].astype(str).str.contains(q, case=False)]
    if categoria:
        df = df[df['Division'] == categoria]
    if genero:
        df = df[df['Genero'] == genero]
    if deporte:
        df = df[df['Deporte'] == deporte]
        
    productos = df.drop_duplicates(subset=['Referencia']).to_dict(orient="records")
    
    filtros = {
        "categorias": sorted([str(x) for x in df_all["Division"].unique()]),
        "generos": sorted([str(x) for x in df_all["Genero"].unique()]),
        "deportes": sorted([str(x) for x in df_all["Deporte"].unique()])
    }
    
    return templates.TemplateResponse(request, "home.html", {
        "productos": productos, 
        "filtros": filtros,
        "query": q,
        "sel_cat": categoria,
        "sel_gen": genero,
        "sel_dep": deporte
    })

@router.get("/producto/{referencia}", response_class=HTMLResponse)
async def detalle_producto(request: Request, referencia: str):
    df = load_data()
    # Asegurar que Referencia sea tratada como string para la comparación
    variantes = df[df['Referencia'].astype(str) == str(referencia)]
    if variantes.empty:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    producto = variantes.iloc[0].to_dict()
    tallas = variantes[['Talla', 'Inventario']].to_dict(orient="records")
    
    return templates.TemplateResponse(request, "info.html", {
        "producto": producto,
        "tallas": tallas
    })
