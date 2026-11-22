"""
Suite de Pruebas Automatizadas para la Plataforma Web de Dengue (Streamlit/Plotly).
"""

import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import numpy as np
import plotly.graph_objects as go

from src.config import (
    ALGORITMOS_DISPONIBLES,
    ARCHIVO_CATALOGO,
    ARCHIVO_COMPARACION,
)
from src.data_loader import (
    cargar_catalogo,
    cargar_predicciones,
    cargar_ranking_algoritmos,
    resolver_ruta_prediccion,
)
from src.data_processor import (
    filtrar_datos,
    calcular_kpis,
    obtener_serie_semanal,
    obtener_distribucion_semanal,
)
from src.plots import (
    plot_evolucion_semanal,
    plot_real_vs_prediccion,
    plot_distribucion_semanal,
    plot_ranking_metrica,
)


class TestDengueWebPlatform(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.catalogo = cargar_catalogo()
        cls.df_lgb = cargar_predicciones("LightGBM")
        cls.df_ranking = cargar_ranking_algoritmos()

    # 1. Archivos requeridos
    def test_01_archivos_requeridos(self):
        self.assertTrue(ARCHIVO_CATALOGO.exists())
        self.assertTrue(ARCHIVO_COMPARACION.exists())
        for alg in ALGORITMOS_DISPONIBLES:
            ruta = resolver_ruta_prediccion(alg)
            self.assertIsNotNone(ruta, f"Archivo no encontrado para {alg}")
            self.assertTrue(ruta.exists())

    # 2. Catálogo de UBIGEOs
    def test_02_catalogo_ubigeos(self):
        self.assertFalse(self.catalogo.empty)
        # Todos los UBIGEO deben tener exactamente 6 dígitos
        longitudes = self.catalogo["ubigeo"].str.len().unique()
        self.assertEqual(list(longitudes), [6])
        self.assertGreaterEqual(len(self.catalogo), 600)

    # 3. Predicciones LightGBM
    def test_03_predicciones_lightgbm(self):
        self.assertEqual(len(self.df_lgb), 6114)
        cols_esperadas = {"ubigeo", "fecha", "ano", "semana", "casos", "prediccion", "departamento", "provincia", "distrito"}
        self.assertTrue(cols_esperadas.issubset(set(self.df_lgb.columns)))
        # No negatividad
        self.assertTrue((self.df_lgb["prediccion"] >= 0).all())
        # Sin nulos en variables clave
        self.assertEqual(self.df_lgb[["casos", "prediccion", "semana"]].isna().sum().sum(), 0)

    # 4. Integridad de semanas epidemiológicas
    def test_04_integridad_semanas(self):
        semanas = self.df_lgb["semana"].unique()
        self.assertEqual(len(semanas), 52)
        self.assertEqual(semanas.min(), 1)
        self.assertEqual(semanas.max(), 52)
        # Sin duplicados
        dups = self.df_lgb.duplicated(subset=["ubigeo", "semana"]).sum()
        self.assertEqual(dups, 0)

    # 5. Filtrado en cascada
    def test_05_filtrado_cascada(self):
        df_loreto = filtrar_datos(self.df_lgb, departamento="LORETO")
        self.assertFalse(df_loreto.empty)
        self.assertTrue((df_loreto["departamento"] == "LORETO").all())

        df_maynas = filtrar_datos(self.df_lgb, departamento="LORETO", provincia="MAYNAS")
        self.assertFalse(df_maynas.empty)
        self.assertTrue((df_maynas["provincia"] == "MAYNAS").all())
        self.assertLess(len(df_maynas), len(df_loreto))

        df_iquitos = filtrar_datos(self.df_lgb, departamento="LORETO", provincia="MAYNAS", distrito="IQUITOS")
        self.assertFalse(df_iquitos.empty)
        self.assertTrue((df_iquitos["distrito"] == "IQUITOS").all())
        self.assertLess(len(df_iquitos), len(df_maynas))

    # 6. Cálculo de KPIs Nacionales (Todas las semanas)
    def test_06_kpis_nacionales(self):
        kpis = calcular_kpis(self.df_lgb, semana_seleccionada=None)
        self.assertAlmostEqual(kpis["total_real"], 35516.0, places=0)
        self.assertAlmostEqual(kpis["total_pred"], 36443.2, places=1)
        self.assertAlmostEqual(kpis["mae"], 2.308, places=2)
        self.assertAlmostEqual(kpis["wape"], 39.74, places=1)
        self.assertEqual(kpis["pico_semana"], 14)
        self.assertAlmostEqual(kpis["pico_casos"], 1782.0, places=0)

    # 7. Cálculo de KPIs puntuales por semana (SE 14)
    def test_07_kpis_semana_especifica(self):
        kpis_sem14 = calcular_kpis(self.df_lgb, semana_seleccionada=14)
        self.assertAlmostEqual(kpis_sem14["total_real"], 1782.0, places=0)
        self.assertAlmostEqual(kpis_sem14["total_pred"], 1491.6, places=1)
        # El MAE puntual debe reflejar la semana 14 (no el MAE global)
        self.assertAlmostEqual(kpis_sem14["mae"], 3.926, places=2)
        self.assertNotEqual(kpis_sem14["mae"], 2.308)

    # 8. Gráfico de líneas conserva todas las semanas (SE 1 a SE 52)
    def test_08_lineas_conservan_52_semanas(self):
        df_sem = obtener_serie_semanal(self.df_lgb)
        self.assertEqual(len(df_sem), 52)
        fig_linea = plot_evolucion_semanal(df_sem, titulo_ambito="Nivel Nacional (Perú)")
        self.assertIsInstance(fig_linea, go.Figure)
        # Verificar que tiene los dos traces: Casos reales y Casos predichos
        nombres = [t.name for t in fig_linea.data]
        self.assertIn("Casos reales", nombres)
        self.assertIn("Casos predichos", nombres)
        # Verificar rango de eje X
        x_range = fig_linea.layout.xaxis.range
        self.assertEqual(x_range, (0.5, 52.5))

    # 9. Gráfico de barras responde a la semana seleccionada
    def test_09_barras_responden_a_semana(self):
        # Todas las semanas
        fig_todas = plot_real_vs_prediccion(35516.0, 36443.2, semana_seleccionada=None)
        self.assertIn("Todas las Semanas", fig_todas.layout.title.text)

        # Semana específica
        fig_sem14 = plot_real_vs_prediccion(1782.0, 1491.6, semana_seleccionada=14)
        self.assertIn("SE 14", fig_sem14.layout.title.text)

    # 10. Ranking de benchmark
    def test_10_ranking_benchmark(self):
        self.assertGreaterEqual(len(self.df_ranking), 16)
        # LightGBM debe ser el puesto 1 por MAE
        top_1 = self.df_ranking.iloc[0]
        self.assertEqual(top_1["Algoritmo"], "LightGBM")
        self.assertAlmostEqual(top_1["MAE"], 2.308, places=2)
        self.assertAlmostEqual(top_1["WAPE"], 39.74, places=1)

        # Extra Trees en puesto 2
        top_2 = self.df_ranking.iloc[1]
        self.assertEqual(top_2["Algoritmo"], "Extra Trees")
        self.assertAlmostEqual(top_2["MAE"], 2.333, places=2)
        self.assertAlmostEqual(top_2["RMSE"], 5.756, places=2)

        # Random Forest en puesto 3
        top_3 = self.df_ranking.iloc[2]
        self.assertEqual(top_3["Algoritmo"], "Random Forest")
        self.assertAlmostEqual(top_3["MAE"], 2.372, places=2)

    # 11. Generación correcta de figuras Plotly
    def test_11_generacion_plots(self):
        df_dist = obtener_distribucion_semanal(self.df_lgb)
        fig_dist = plot_distribucion_semanal(df_dist)
        self.assertIsInstance(fig_dist, go.Figure)

        fig_mae = plot_ranking_metrica(self.df_ranking, "MAE", "MAE", " casos")
        self.assertIsInstance(fig_mae, go.Figure)

        fig_wape = plot_ranking_metrica(self.df_ranking, "WAPE", "WAPE", "%")
        self.assertIsInstance(fig_wape, go.Figure)


if __name__ == "__main__":
    unittest.main(verbosity=2)
