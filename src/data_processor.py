"""
Módulo de filtrado y cálculo de indicadores epidemiológicos y métricas de error.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


def filtrar_datos(
    df: pd.DataFrame,
    departamento: Optional[str] = None,
    provincia: Optional[str] = None,
    distrito: Optional[str] = None,
    ano: Optional[int] = None,
    semana: Optional[int] = None,
) -> pd.DataFrame:
    """
    Aplica filtros geográficos y temporales en cascada.
    """
    datos = df.copy()

    if departamento is not None and departamento != "Todos":
        datos = datos[datos["departamento"] == departamento]

    if provincia is not None and provincia != "Todas":
        datos = datos[datos["provincia"] == provincia]

    if distrito is not None and distrito != "Todos":
        datos = datos[datos["distrito"] == distrito]

    if ano is not None:
        datos = datos[datos["ano"] == ano]

    if semana is not None:
        datos = datos[datos["semana"] == semana]

    return datos


def calcular_kpis(
    df_filtrado_geo: pd.DataFrame,
    semana_seleccionada: Optional[int] = None
) -> Dict[str, Any]:
    """
    Calcula las métricas epidemiológicas (Casos Reales, Predichos, MAE, WAPE, RMSE, Pico).
    Calcula el MAE real y específico para el ámbito y semana consultados,
    sin presentar valores globales estáticos.
    """
    if df_filtrado_geo.empty:
        return {
            "total_real": 0.0,
            "total_pred": 0.0,
            "mae": 0.0,
            "rmse": 0.0,
            "wape": 0.0,
            "pico_semana": None,
            "pico_casos": 0.0,
            "semanas_observadas": 0,
            "distritos_observados": 0,
            "sin_datos": True,
        }

    # Identificar la semana epidemiológica de mayor incidencia en el ámbito geográfico
    resumen_semanas = (
        df_filtrado_geo.groupby("semana")["casos"]
        .sum()
        .sort_values(ascending=False)
    )

    if not resumen_semanas.empty:
        pico_semana = int(resumen_semanas.index[0])
        pico_casos = float(resumen_semanas.iloc[0])
    else:
        pico_semana = None
        pico_casos = 0.0

    # Determinar el subconjunto de evaluación: semana específica o todas las semanas
    datos_analisis = df_filtrado_geo
    if semana_seleccionada is not None:
        datos_analisis = df_filtrado_geo[df_filtrado_geo["semana"] == semana_seleccionada]

    if datos_analisis.empty:
        return {
            "total_real": 0.0,
            "total_pred": 0.0,
            "mae": 0.0,
            "rmse": 0.0,
            "wape": 0.0,
            "pico_semana": pico_semana,
            "pico_casos": pico_casos,
            "semanas_observadas": 0,
            "distritos_observados": 0,
            "sin_datos": True,
        }

    real = float(datos_analisis["casos"].sum())
    pred = float(datos_analisis["prediccion"].sum())

    # Error Absoluto Medio (MAE) específico del subconjunto analizado
    mae = float(datos_analisis["error_absoluto"].mean())

    # RMSE
    rmse = float(np.sqrt((datos_analisis["error"] ** 2).mean()))

    # WAPE (%): Sum(|real - pred|) / Sum(real) * 100
    if real > 0:
        wape = float(datos_analisis["error_absoluto"].sum() / real * 100.0)
    else:
        wape = 0.0

    return {
        "total_real": real,
        "total_pred": pred,
        "mae": mae,
        "rmse": rmse,
        "wape": wape,
        "pico_semana": pico_semana,
        "pico_casos": pico_casos,
        "semanas_observadas": int(df_filtrado_geo["semana"].nunique()),
        "distritos_observados": int(df_filtrado_geo["ubigeo"].nunique()),
        "sin_datos": False,
    }


def obtener_serie_semanal(df_filtrado_geo: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa las semanas epidemiológicas observadas sin agregar artificialmente
    semanas con cero casos.
    """
    if df_filtrado_geo.empty:
        return pd.DataFrame(columns=["semana", "casos", "prediccion", "diferencia", "error_abs"])

    agrupado = (
        df_filtrado_geo.groupby("semana")
        .agg(
            casos=("casos", "sum"),
            prediccion=("prediccion", "sum"),
            error_abs=("error_absoluto", "sum"),
        )
        .reset_index()
    )

    agrupado["diferencia"] = agrupado["casos"] - agrupado["prediccion"]
    agrupado = agrupado.sort_values("semana").reset_index(drop=True)
    return agrupado


def obtener_distribucion_semanal(df_filtrado_geo: pd.DataFrame) -> pd.DataFrame:
    """
    Distribución de casos por semana para análisis epidemiológico de volumen.
    Categoriza niveles descriptivos transparentes basados en percentiles observados,
    sin inventar umbrales oficiales no documentados.
    """
    serie = obtener_serie_semanal(df_filtrado_geo)
    if serie.empty:
        return serie

    total = serie["casos"].sum()
    serie["porcentaje"] = (serie["casos"] / total * 100.0) if total > 0 else 0.0

    p50 = serie["casos"].quantile(0.50)
    p80 = serie["casos"].quantile(0.80)

    def categorizar_volumen(v):
        if v >= p80 and v > 0:
            return "Volumen alto (Picos)"
        elif v >= p50 and v > 0:
            return "Volumen moderado"
        else:
            return "Volumen bajo"

    serie["categoria_volumen"] = serie["casos"].apply(categorizar_volumen)
    return serie
