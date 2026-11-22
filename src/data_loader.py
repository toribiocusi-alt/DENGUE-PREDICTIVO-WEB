"""
Módulo de carga y almacenamiento en caché de datos epidemiológicos y predicciones.
Optimizado para Streamlit Community Cloud.
"""

from pathlib import Path
from typing import Optional
import pandas as pd
import numpy as np
import streamlit as st

from .config import (
    DATA_DIR,
    ARCHIVO_CATALOGO,
    ARCHIVO_COMPARACION,
)


@st.cache_data(show_spinner=False)
def cargar_catalogo() -> pd.DataFrame:
    """
    Carga el catálogo geográfico de UBIGEOs normalizado (662 distritos).
    """
    if not ARCHIVO_CATALOGO.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo de catálogo: {ARCHIVO_CATALOGO}"
        )

    df_cat = pd.read_csv(ARCHIVO_CATALOGO, dtype=str)
    df_cat["ubigeo"] = (
        df_cat["ubigeo"]
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.strip()
        .str.zfill(6)
    )

    for col in ["departamento", "provincia", "distrito"]:
        if col in df_cat.columns:
            df_cat[col] = df_cat[col].astype(str).str.strip().str.upper()

    return df_cat


def resolver_ruta_prediccion(algoritmo: str) -> Optional[Path]:
    """
    Determina la ruta física del archivo CSV correspondiente a un algoritmo.
    """
    nombre_limpio = algoritmo.strip().lower()
    slug_underscore = nombre_limpio.replace(" ", "_")
    slug_compact = nombre_limpio.replace(" ", "")

    candidatos = [
        DATA_DIR / f"predicciones_2025_{slug_underscore}.csv",
        DATA_DIR / f"predicciones_2025_{slug_compact}.csv",
    ]

    for c in candidatos:
        if c.exists():
            return c

    return None


@st.cache_data(show_spinner=False)
def cargar_predicciones(algoritmo: str) -> pd.DataFrame:
    """
    Carga y valida las predicciones 2025 de un algoritmo específico,
    incorporando la correspondencia geográfica por UBIGEO.
    """
    ruta = resolver_ruta_prediccion(algoritmo)
    if ruta is None:
        raise FileNotFoundError(
            f"No se encontró el archivo de predicciones para el algoritmo '{algoritmo}'."
        )

    # Carga con tipo string en ubigeo para preservar ceros a la izquierda
    df = pd.read_csv(ruta, dtype={"ubigeo": str})
    df.columns = df.columns.str.strip().str.lower()

    columnas_esperadas = ["ubigeo", "fecha", "ano", "semana", "casos", "prediccion"]
    faltantes = [c for c in columnas_esperadas if c not in df.columns]
    if faltantes:
        raise ValueError(
            f"El archivo {ruta.name} no contiene las columnas requeridas: {faltantes}"
        )

    # Normalización estricta de UBIGEO a 6 dígitos
    df["ubigeo"] = (
        df["ubigeo"]
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.strip()
        .str.zfill(6)
    )

    df["ano"] = pd.to_numeric(df["ano"], errors="coerce").fillna(2025).astype(int)
    df["semana"] = pd.to_numeric(df["semana"], errors="coerce").astype(int)
    df["casos"] = pd.to_numeric(df["casos"], errors="coerce").fillna(0.0)
    df["prediccion"] = pd.to_numeric(df["prediccion"], errors="coerce").fillna(0.0)

    # Restricción de no negatividad biológica
    df["prediccion"] = np.maximum(0.0, df["prediccion"])

    # Cálculo de errores individuales
    df["error_absoluto"] = (df["casos"] - df["prediccion"]).abs()
    df["error"] = df["prediccion"] - df["casos"]

    # Incorporar información geográfica
    catalogo = cargar_catalogo()
    df = df.merge(
        catalogo[["ubigeo", "departamento", "provincia", "distrito"]],
        on="ubigeo",
        how="left"
    )

    df["departamento"] = df["departamento"].fillna("DESCONOCIDO")
    df["provincia"] = df["provincia"].fillna("DESCONOCIDO")
    df["distrito"] = df["distrito"].fillna("DESCONOCIDO")

    return df


@st.cache_data(show_spinner=False)
def cargar_ranking_algoritmos() -> pd.DataFrame:
    """
    Carga los resultados de evaluación experimental de todos los modelos (2025),
    ordenados por MAE ascendente.
    """
    if not ARCHIVO_COMPARACION.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo de comparación: {ARCHIVO_COMPARACION}"
        )

    df = pd.read_csv(ARCHIVO_COMPARACION)
    df.columns = df.columns.str.strip()

    col_wape = [c for c in df.columns if "WAPE" in c.upper()]
    if col_wape:
        df = df.rename(columns={col_wape[0]: "WAPE"})

    for col in ["MAE", "RMSE", "WAPE"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values("MAE", ascending=True).reset_index(drop=True)

    df["tiene_archivo"] = df["Algoritmo"].apply(
        lambda alg: resolver_ruta_prediccion(alg) is not None
    )

    return df
