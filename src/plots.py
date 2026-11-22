"""
Módulo de generación de gráficos interactivos con Plotly para entorno Web.
"""

from typing import Optional
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from .config import (
    PANEL, BORDE, TEXTO, SECUNDARIO, CELESTE, NARANJA, VERDE, ROJO, AMARILLO
)


def _configurar_layout_base(fig: go.Figure, titulo: str, altura: int = 400) -> go.Figure:
    """Aplica la configuración oscura y tipografía consistente a una figura Plotly."""
    fig.update_layout(
        title=dict(
            text=f"<b>{titulo}</b>",
            font=dict(color=TEXTO, size=14, family="Segoe UI, sans-serif"),
            x=0.01,
            y=0.96
        ),
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(color=TEXTO, family="Segoe UI, sans-serif"),
        height=altura,
        margin=dict(l=45, r=30, t=55, b=45),
        legend=dict(
            bgcolor="rgba(23, 36, 58, 0.8)",
            bordercolor=BORDE,
            borderwidth=1,
            font=dict(size=11, color=TEXTO),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hoverlabel=dict(
            bgcolor="#1C2B45",
            bordercolor=BORDE,
            font=dict(color=TEXTO, size=12)
        )
    )
    fig.update_xaxes(
        gridcolor=BORDE,
        zerolinecolor=BORDE,
        tickfont=dict(color=SECUNDARIO, size=10),
        title_font=dict(color=SECUNDARIO, size=11)
    )
    fig.update_yaxes(
        gridcolor=BORDE,
        zerolinecolor=BORDE,
        tickfont=dict(color=SECUNDARIO, size=10),
        title_font=dict(color=SECUNDARIO, size=11)
    )
    return fig


def plot_evolucion_semanal(
    df_semanal: pd.DataFrame,
    titulo_ambito: str = "Nivel Nacional (Perú)"
) -> go.Figure:
    """
    Gráfico 1: Evolución semanal mediante líneas (Plotly).
    - Muestra todas las semanas epidemiológicas disponibles de 2025 (SE 1 a SE 52).
    - Dos líneas: casos reales y casos predichos.
    - Conserva siempre la visualización de las 52 semanas.
    """
    fig = go.Figure()

    if df_semanal.empty:
        fig.add_annotation(
            text="No se registran casos para el ámbito seleccionado",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color=SECUNDARIO, size=14)
        )
        return _configurar_layout_base(fig, f"Evolución Semanal — {titulo_ambito}", 420)

    semanas = df_semanal["semana"]
    reales = df_semanal["casos"]
    predichos = df_semanal["prediccion"]

    # Línea de casos reales
    fig.add_trace(go.Scatter(
        x=semanas,
        y=reales,
        name="Casos reales",
        mode="lines+markers",
        line=dict(color=CELESTE, width=2.4),
        marker=dict(size=6, color=CELESTE, symbol="circle"),
        hovertemplate="<b>SE %{x}</b><br>Casos reales: %{y:,.0f}<extra></extra>"
    ))

    # Línea de casos predichos
    fig.add_trace(go.Scatter(
        x=semanas,
        y=predichos,
        name="Casos predichos",
        mode="lines+markers",
        line=dict(color=NARANJA, width=2.0, dash="dash"),
        marker=dict(size=5, color=NARANJA, symbol="square"),
        hovertemplate="<b>SE %{x}</b><br>Predicción ML: %{y:,.1f}<extra></extra>"
    ))

    # Identificar y anotar pico epidemiológico
    idx_pico = int(np.argmax(reales.values))
    sem_pico = semanas.iloc[idx_pico]
    val_pico = reales.iloc[idx_pico]

    if val_pico > 0:
        fig.add_annotation(
            x=sem_pico,
            y=val_pico,
            text=f"Pico: SE {sem_pico} ({val_pico:,.0f} casos)",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1.5,
            arrowcolor=ROJO,
            ax=0,
            ay=-35,
            bgcolor="#17243A",
            bordercolor=BORDE,
            borderwidth=1,
            font=dict(color=TEXTO, size=10, family="Segoe UI")
        )

    # Configuración de Ejes (Asegurando el horizonte completo de SE 1 a SE 52)
    fig.update_xaxes(
        title_text="Semana Epidemiológica (SE)",
        range=[0.5, 52.5],
        tickmode="array",
        tickvals=[1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 52],
        ticktext=["SE 1", "SE 5", "SE 10", "SE 15", "SE 20", "SE 25", "SE 30", "SE 35", "SE 40", "SE 45", "SE 50", "SE 52"]
    )
    fig.update_yaxes(
        title_text="Cantidad de Casos",
        tickformat=","
    )

    titulo = f"Evolución Semanal de Casos — {titulo_ambito} (SE 1 a SE 52 · 2025)"
    return _configurar_layout_base(fig, titulo, 420)


def plot_real_vs_prediccion(
    real: float,
    pred: float,
    semana_seleccionada: Optional[int] = None
) -> go.Figure:
    """
    Gráfico 2: Comparación mediante barras (Plotly).
    - Dos barras: casos reales y casos predichos.
    - Con semana específica: compara únicamente esa semana.
    - Con Todas las semanas: muestra el acumulado anual de todas las semanas.
    """
    etiquetas = ["Casos Reales", "Casos Predichos"]
    valores = [real, pred]
    colores = [CELESTE, NARANJA]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=etiquetas,
        y=valores,
        marker=dict(color=colores, line=dict(color=BORDE, width=1.2)),
        text=[f"{real:,.0f}", f"{pred:,.1f}"],
        textposition="outside",
        textfont=dict(color=TEXTO, size=12, family="Segoe UI"),
        hovertemplate="<b>%{x}</b>: %{y:,.1f} casos<extra></extra>",
        width=0.48
    ))

    # Cálculo de discrepancia
    diferencia = pred - real
    signo = "+" if diferencia > 0 else ""
    error_pct = (abs(diferencia) / real * 100) if real > 0 else 0.0

    if semana_seleccionada is not None:
        subtitulo = f"SE {semana_seleccionada}"
        titulo = f"Comparación Real vs. Predicción · SE {semana_seleccionada}"
    else:
        subtitulo = "Todas las Semanas (Acumulado 2025)"
        titulo = "Comparación Real vs. Predicción · Todas las Semanas"

    fig.add_annotation(
        text=f"Diferencia: <b>{signo}{diferencia:,.1f}</b> ({error_pct:.1f}% desv.)",
        xref="paper", yref="paper",
        x=0.5, y=0.96, showarrow=False,
        bgcolor="#17243A",
        bordercolor=BORDE,
        borderwidth=1,
        font=dict(color=VERDE if error_pct <= 25 else NARANJA, size=11)
    )

    max_y = max(valores) if max(valores) > 0 else 10
    fig.update_yaxes(
        title_text="Cantidad de Casos",
        range=[0, max_y * 1.30 + 1],
        tickformat=","
    )
    fig.update_xaxes(title_text="")

    fig.update_layout(showlegend=False)
    return _configurar_layout_base(fig, titulo, 420)


def plot_distribucion_semanal(df_dist: pd.DataFrame) -> go.Figure:
    """
    Visualización adicional de la distribución semanal de casos.
    Muestra la concentración semanal y la curva epidémica observada.
    """
    fig = go.Figure()

    if df_dist.empty:
        fig.add_annotation(
            text="Sin datos de distribución para el filtro seleccionado",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color=SECUNDARIO, size=13)
        )
        return _configurar_layout_base(fig, "Distribución Semanal de Incidencia", 350)

    # Mapeo de colores descriptivo y comprensible sin categorías no documentadas
    color_map = {
        "Volumen alto (Picos)": ROJO,
        "Volumen moderado": AMARILLO,
        "Volumen bajo": "#294E73"
    }

    colores = [color_map.get(cat, CELESTE) for cat in df_dist["categoria_volumen"]]

    fig.add_trace(go.Bar(
        x=df_dist["semana"],
        y=df_dist["casos"],
        marker=dict(color=colores, line=dict(color=BORDE, width=0.8)),
        name="Casos reportados",
        hovertemplate="<b>SE %{x}</b><br>Casos: %{y:,.0f}<br>Nivel: %{customdata}<extra></extra>",
        customdata=df_dist["categoria_volumen"]
    ))

    # Superponer curva de tendencia predicha
    fig.add_trace(go.Scatter(
        x=df_dist["semana"],
        y=df_dist["prediccion"],
        mode="lines",
        name="Tendencia predicha ML",
        line=dict(color=NARANJA, width=2.2, dash="dash"),
        hovertemplate="<b>SE %{x}</b><br>Tendencia predicha: %{y:,.1f}<extra></extra>"
    ))

    fig.update_xaxes(
        title_text="Semana Epidemiológica (SE)",
        range=[0.5, 52.5],
        tickmode="array",
        tickvals=[1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 52],
        ticktext=["SE 1", "SE 5", "SE 10", "SE 15", "SE 20", "SE 25", "SE 30", "SE 35", "SE 40", "SE 45", "SE 50", "SE 52"]
    )
    fig.update_yaxes(
        title_text="Casos Semanales",
        tickformat=","
    )

    return _configurar_layout_base(fig, "Distribución de Incidencia por Semana Epidemiológica (Curva Epidémica 2025)", 350)


def plot_ranking_metrica(
    df_ranking: pd.DataFrame,
    columna_metrica: str,
    titulo_metrica: str,
    unidad: str = ""
) -> go.Figure:
    """
    Gráfico de barras horizontales comparando el desempeño de los modelos.
    """
    df_valido = df_ranking.dropna(subset=[columna_metrica]).sort_values(columna_metrica, ascending=True)

    algoritmos = df_valido["Algoritmo"].tolist()
    valores = df_valido[columna_metrica].tolist()

    colores = []
    for alg in algoritmos:
        if alg == "LightGBM":
            colores.append(VERDE)       # Líder general
        elif alg == "Extra Trees":
            colores.append(CELESTE)     # Mejor RMSE
        elif alg == "Random Forest":
            colores.append(AMARILLO)    # Tercer puesto
        else:
            colores.append("#29415F")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=algoritmos,
        x=valores,
        orientation="h",
        marker=dict(color=colores, line=dict(color=BORDE, width=0.8)),
        text=[f"{v:.2f}{unidad}" for v in valores],
        textposition="outside",
        textfont=dict(color=TEXTO, size=10),
        hovertemplate="<b>%{y}</b>: %{x:.3f} " + unidad + "<extra></extra>"
    ))

    fig.update_xaxes(title_text=titulo_metrica)
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(showlegend=False)

    return _configurar_layout_base(fig, f"Comparación: {titulo_metrica} (Menor es mejor)", 480)
