"""
=============================================================================
VIGILANCIA Y PREDICCIÓN DE DENGUE EN EL PERÚ — PLATAFORMA WEB PÚBLICA
=============================================================================
Aplicación web interactiva basada en Streamlit y Plotly.
Modelo Campeón: LightGBM
Evaluación retrospectiva: Semanas epidemiológicas 1 a 52 de 2025
=============================================================================
"""

import sys
from pathlib import Path

# Asegurar importación de módulos locales
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
import pandas as pd
import numpy as np

from src.config import (
    ESTILOS_CSS,
    ALGORITMOS_DISPONIBLES,
    ALGORITMO_DEFAULT,
    CELESTE,
    NARANJA,
    VERDE,
    ROJO,
    AMARILLO,
    PURPURA,
    TEXTO,
    SECUNDARIO,
)
from src.data_loader import (
    cargar_catalogo,
    cargar_predicciones,
    cargar_ranking_algoritmos,
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


# =============================================================================
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO
# =============================================================================

st.set_page_config(
    page_title="Vigilancia y Predicción de Dengue — Perú",
    page_icon="🦟",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(ESTILOS_CSS, unsafe_allow_html=True)

# Inicializar estado de sesión
if "algoritmo_seleccionado" not in st.session_state:
    st.session_state.algoritmo_seleccionado = ALGORITMO_DEFAULT


# =============================================================================
# 2. ENCABEZADO INSTITUCIONAL
# =============================================================================

algoritmo_actual = st.session_state.algoritmo_seleccionado

st.markdown(f"""
<div class="header-box">
    <div>
        <h1 class="header-title">🇵🇪 VIGILANCIA Y PREDICCIÓN DE DENGUE — PERÚ</h1>
        <p class="header-subtitle">
            Plataforma interactiva de vigilancia epidemiológica semanal y evaluación de modelos de Machine Learning (2025)
        </p>
    </div>
    <div style="display: flex; gap: 8px;">
        <span class="header-badge-cyan">SEMANAS EPIDEMIOLÓGICAS (SE 1 - 52) · 2025</span>
        <span class="header-badge">MODELO ACTIVO: {algoritmo_actual.upper()}</span>
    </div>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# 3. CARGA DE DATOS CENTRALIZADA
# =============================================================================

try:
    catalogo = cargar_catalogo()
    df_pred = cargar_predicciones(algoritmo_actual)
    df_ranking = cargar_ranking_algoritmos()
except Exception as e:
    st.error(f"Error al inicializar los datos: {e}")
    st.stop()


# =============================================================================
# 4. PESTAÑAS PRINCIPALES
# =============================================================================

tab_vigilancia, tab_benchmark = st.tabs([
    "📊 Vigilancia y Predicción Epidemiológica",
    "🏆 Comparación de Algoritmos (Benchmark 2025)"
])


# =============================================================================
# TAB 1: VIGILANCIA Y PREDICCIÓN
# =============================================================================

with tab_vigilancia:

    # A. PANEL DE FILTROS EN CASCADA
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns([1.2, 1.2, 1.2, 0.7, 1.1, 1.2])

    with c1:
        st.markdown('<p class="filter-label">Departamento</p>', unsafe_allow_html=True)
        deptos = ["Todos"] + sorted(
            [d for d in df_pred["departamento"].dropna().unique() if d != "DESCONOCIDO"]
        )
        depto_sel = st.selectbox("Departamento", deptos, label_visibility="collapsed")

    # Filtrado intermedio para cascada
    df_dpto = df_pred if depto_sel == "Todos" else df_pred[df_pred["departamento"] == depto_sel]

    with c2:
        st.markdown('<p class="filter-label">Provincia</p>', unsafe_allow_html=True)
        provs = ["Todas"] + sorted(
            [p for p in df_dpto["provincia"].dropna().unique() if p != "DESCONOCIDO"]
        )
        prov_sel = st.selectbox("Provincia", provs, label_visibility="collapsed")

    df_prov = df_dpto if prov_sel == "Todas" else df_dpto[df_dpto["provincia"] == prov_sel]

    with c3:
        st.markdown('<p class="filter-label">Distrito</p>', unsafe_allow_html=True)
        dists = ["Todos"] + sorted(
            [d for d in df_prov["distrito"].dropna().unique() if d != "DESCONOCIDO"]
        )
        dist_sel = st.selectbox("Distrito", dists, label_visibility="collapsed")

    with c4:
        st.markdown('<p class="filter-label">Año</p>', unsafe_allow_html=True)
        st.selectbox("Año", [2025], label_visibility="collapsed")

    with c5:
        st.markdown('<p class="filter-label">Semana Epidemiológica</p>', unsafe_allow_html=True)
        opciones_semana = ["Todas las semanas"] + [f"Semana {s:02d}" for s in range(1, 53)]
        semana_texto = st.selectbox("Semana", opciones_semana, label_visibility="collapsed")

        semana_num = None
        if semana_texto != "Todas las semanas":
            semana_num = int(semana_texto.replace("Semana ", ""))

    with c6:
        st.markdown('<p class="filter-label">Algoritmo Predictivo</p>', unsafe_allow_html=True)
        idx_alg = ALGORITMOS_DISPONIBLES.index(algoritmo_actual) if algoritmo_actual in ALGORITMOS_DISPONIBLES else 0
        nuevo_alg = st.selectbox(
            "Algoritmo",
            ALGORITMOS_DISPONIBLES,
            index=idx_alg,
            label_visibility="collapsed"
        )
        if nuevo_alg != algoritmo_actual:
            st.session_state.algoritmo_seleccionado = nuevo_alg
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # B. OBTENCIÓN DE DATOS FILTRADOS
    # Ámbito geográfico (incluye todas las semanas para la perspectiva anual del gráfico de líneas)
    df_geo = filtrar_datos(
        df_pred,
        departamento=depto_sel,
        provincia=prov_sel,
        distrito=dist_sel,
        ano=2025,
        semana=None
    )

    # Construir título legible del ámbito
    if dist_sel != "Todos":
        titulo_ambito = f"{dist_sel} ({prov_sel}, {depto_sel})"
    elif prov_sel != "Todas":
        titulo_ambito = f"Provincia {prov_sel} ({depto_sel})"
    elif depto_sel != "Todos":
        titulo_ambito = f"Departamento {depto_sel}"
    else:
        titulo_ambito = "Nivel Nacional (Perú)"

    # C. CÁLCULO DE KPIS ESPECÍFICOS DEL SUBCONJUNTO
    kpis = calcular_kpis(df_geo, semana_seleccionada=semana_num)

    # D. TARJETAS KPI (METRIC CARDS)
    k1, k2, k3, k4, k5, k6 = st.columns(6)

    sub_semana = f"SE {semana_num}" if semana_num else "Acumulado Anual"

    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <span class="kpi-title">CASOS REALES</span>
            <span class="kpi-value" style="color: {CELESTE};">{kpis['total_real']:,.0f}</span>
            <span class="kpi-sub">{sub_semana}</span>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <span class="kpi-title">PREDICCIÓN ML</span>
            <span class="kpi-value" style="color: {NARANJA};">{kpis['total_pred']:,.1f}</span>
            <span class="kpi-sub">{algoritmo_actual}</span>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <span class="kpi-title">MAE (ERROR MEDIO)</span>
            <span class="kpi-value" style="color: {VERDE};">{kpis['mae']:.3f}</span>
            <span class="kpi-sub">En ámbito seleccionado</span>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="kpi-card">
            <span class="kpi-title">WAPE</span>
            <span class="kpi-value" style="color: {AMARILLO};">{kpis['wape']:.2f}%</span>
            <span class="kpi-sub">Error ponderado</span>
        </div>
        """, unsafe_allow_html=True)

    with k5:
        st.markdown(f"""
        <div class="kpi-card">
            <span class="kpi-title">RMSE</span>
            <span class="kpi-value" style="color: {PURPURA};">{kpis['rmse']:.2f}</span>
            <span class="kpi-sub">Penalización de picos</span>
        </div>
        """, unsafe_allow_html=True)

    with k6:
        pico_txt = f"Semana {kpis['pico_semana']}" if kpis['pico_semana'] else "SE --"
        pico_sub = f"{kpis['pico_casos']:,.0f} casos" if kpis['pico_semana'] else "Sin registros"
        st.markdown(f"""
        <div class="kpi-card">
            <span class="kpi-title">SEMANA PICO</span>
            <span class="kpi-value" style="color: {ROJO};">{pico_txt}</span>
            <span class="kpi-sub">{pico_sub}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    # E. GRÁFICOS PRINCIPALES
    # Regla: El gráfico de líneas conserva siempre las 52 semanas.
    # El gráfico de barras se actualiza según la semana seleccionada.
    col_linea, col_barras = st.columns([1.6, 1.0])

    df_semanal = obtener_serie_semanal(df_geo)

    with col_linea:
        fig_linea = plot_evolucion_semanal(df_semanal, titulo_ambito=titulo_ambito)
        st.plotly_chart(fig_linea, use_container_width=True)

    with col_barras:
        fig_barras = plot_real_vs_prediccion(
            real=kpis["total_real"],
            pred=kpis["total_pred"],
            semana_seleccionada=semana_num
        )
        st.plotly_chart(fig_barras, use_container_width=True)

    # F. GRÁFICO ADICIONAL: DISTRIBUCIÓN SEMANAL (CURVA EPIDÉMICA)
    df_dist = obtener_distribucion_semanal(df_geo)
    fig_dist = plot_distribucion_semanal(df_dist)
    st.plotly_chart(fig_dist, use_container_width=True)

    # G. PIE DE PÁGINA INFORMATIVO
    st.markdown("""
    <div class="footer-text">
        Fuente: Datos abiertos de vigilancia de dengue (MINSA / CDC Perú) y modelos predictivos 2025.
        <br><b>Nota metodológica:</b> Los valores corresponden a una evaluación retrospectiva del año 2025,
        no a un pronóstico en tiempo real hacia el futuro.
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# TAB 2: COMPARACIÓN DE ALGORITMOS (BENCHMARK)
# =============================================================================

with tab_benchmark:

    # Banner de contexto experimental
    st.markdown("""
    <div class="info-box">
        <b>🔬 METODOLOGÍA DEL EXPERIMENTO MACHINE LEARNING:</b><br>
        Los 16 algoritmos fueron entrenados con el histórico 2000-2023, ajustados en validación con 2024 y
        evaluados de forma ciega sobre las 52 semanas epidemiológicas de 2025 en 432 distritos endémicos.
        Se aplicaron modelos de ensamble (Random Forest, Extra Trees, Gradient Boosting), modelos lineales regularizados,
        modelos con enlaces Poisson/Tweedie y máquinas de soporte vectorial.
    </div>
    """, unsafe_allow_html=True)

    # Tarjetas destacadas de podio
    b1, b2, b3 = st.columns(3)

    with b1:
        st.markdown(f"""
        <div class="kpi-card" style="border-left: 4px solid {VERDE};">
            <span class="kpi-title">🏆 CANDIDATO LÍDER (MAE & WAPE)</span>
            <span class="kpi-value" style="color: {VERDE};">LightGBM</span>
            <span class="kpi-sub">MAE: 2.308 | WAPE: 39.74% | RMSE: 5.999</span>
        </div>
        """, unsafe_allow_html=True)

    with b2:
        st.markdown(f"""
        <div class="kpi-card" style="border-left: 4px solid {CELESTE};">
            <span class="kpi-title">🎯 MEJOR RMSE (PRECISIÓN EN PICOS)</span>
            <span class="kpi-value" style="color: {CELESTE};">Extra Trees</span>
            <span class="kpi-sub">RMSE: 5.756 | MAE: 2.333 | WAPE: 40.16%</span>
        </div>
        """, unsafe_allow_html=True)

    with b3:
        st.markdown(f"""
        <div class="kpi-card" style="border-left: 4px solid {AMARILLO};">
            <span class="kpi-title">🌲 TERCER LUGAR ENSEMBLE</span>
            <span class="kpi-value" style="color: {AMARILLO};">Random Forest</span>
            <span class="kpi-sub">MAE: 2.372 | RMSE: 5.793 | WAPE: 40.83%</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    # Tabla y Gráficos comparativos
    col_ranking_tbl, col_ranking_plot = st.columns([1.1, 1.3])

    with col_ranking_tbl:
        st.markdown("### 📋 Ranking General de Modelos")

        # Preparar tabla con formato limpio
        df_mostrar = df_ranking.copy()
        df_mostrar.insert(0, "Puesto", range(1, len(df_mostrar) + 1))
        df_mostrar["MAE"] = df_mostrar["MAE"].map(lambda x: f"{x:.3f}")
        df_mostrar["RMSE"] = df_mostrar["RMSE"].map(lambda x: f"{x:.3f}")
        df_mostrar["WAPE (%)"] = df_mostrar["WAPE"].map(lambda x: f"{x:.2f}%")

        columnas_tabla = ["Puesto", "Algoritmo", "MAE", "RMSE", "WAPE (%)"]
        st.dataframe(
            df_mostrar[columnas_tabla],
            use_container_width=True,
            hide_index=True,
            height=490
        )

        # Selector rápido para cambiar de modelo desde el benchmark
        st.markdown("#### ⚡ Seleccionar Modelo para el Dashboard")
        algos_con_archivo = df_ranking[df_ranking["tiene_archivo"]]["Algoritmo"].tolist()
        alg_elegido = st.selectbox(
            "Elegir algoritmo:",
            algos_con_archivo,
            index=algos_con_archivo.index(algoritmo_actual) if algoritmo_actual in algos_con_archivo else 0,
            key="sel_benchmark"
        )
        if st.button("🚀 Aplicar este modelo al Dashboard"):
            st.session_state.algoritmo_seleccionado = alg_elegido
            st.rerun()

    with col_ranking_plot:
        st.markdown("### 📊 Gráficos Comparativos Interactivos")
        opcion_metrica = st.radio(
            "Visualizar métrica:",
            ["MAE (Error Absoluto Medio)", "WAPE (Error Porcentual)", "RMSE (Raíz del Error Cuadrático)"],
            horizontal=True
        )

        if "MAE" in opcion_metrica:
            fig_metrica = plot_ranking_metrica(df_ranking, "MAE", "Error Absoluto Medio (MAE)", unidad=" casos")
        elif "WAPE" in opcion_metrica:
            fig_metrica = plot_ranking_metrica(df_ranking, "WAPE", "Error Porcentual Ponderado (WAPE)", unidad="%")
        else:
            fig_metrica = plot_ranking_metrica(df_ranking, "RMSE", "RMSE (Sensible a Picos)", unidad=" casos")

        st.plotly_chart(fig_metrica, use_container_width=True)
