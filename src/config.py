"""
Configuración general, paleta de colores, rutas y estilos CSS para Streamlit.
"""

from pathlib import Path

# Rutas de datos
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

ARCHIVO_CATALOGO = DATA_DIR / "catalogo_ubigeos.csv"
ARCHIVO_COMPARACION = DATA_DIR / "comparacion_algoritmos_dengue_2025.csv"

# Paleta Dark Theme profesional
FONDO = "#0B1020"       # Fondo global de la aplicación
PANEL = "#17243A"       # Superficie de tarjetas KPI y contenedores
PANEL_ALT = "#1C2B45"   # Superficie alterna o activa
BORDE = "#263750"       # Bordes sutiles
TEXTO = "#E8EEF8"       # Texto principal de alta legibilidad
SECUNDARIO = "#91A4BE"  # Subtítulos, etiquetas y ejes
CELESTE = "#20C4E8"     # Casos Reales (Color institucional)
NARANJA = "#FF9F43"     # Casos Predichos (Machine Learning)
VERDE = "#35D39A"       # Modelo Campeón / MAE óptimo
ROJO = "#FF6B6B"        # Pico de transmisión / Alerta
AMARILLO = "#FEE75C"    # Intensidad moderada
PURPURA = "#A29BFE"     # Métricas secundarias

# Algoritmos disponibles
ALGORITMOS_DISPONIBLES = [
    "LightGBM",
    "Extra Trees",
    "Random Forest",
    "XGBoost",
    "Gradient Boosting",
    "ElasticNet",
    "Lasso",
    "Decision Tree",
    "Ridge",
    "Regresion Lineal",
    "SVR",
    "KNN",
    "NuSVR",
    "AdaBoost",
    "Tweedie",
    "Poisson",
]

ALGORITMO_DEFAULT = "LightGBM"

# Hoja de estilos CSS optimizada para Streamlit (inspirada en la app de extorsiones)
ESTILOS_CSS = f"""
<style>
    /* Estructura base de la aplicación */
    .stApp {{
        background-color: {FONDO};
        color: {TEXTO};
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }}

    header[data-testid="stHeader"] {{
        background-color: {FONDO} !important;
    }}

    /* Contenedor principal con márgenes controlados */
    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1600px;
    }}

    /* Encabezado */
    .header-box {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        flex-wrap: wrap;
        gap: 10px;
    }}

    .header-title {{
        color: {TEXTO};
        font-size: 24px;
        font-weight: 800;
        letter-spacing: -0.4px;
        margin: 0;
        padding: 0;
    }}

    .header-subtitle {{
        color: {SECUNDARIO};
        font-size: 13px;
        margin-top: 4px;
        margin-bottom: 0;
    }}

    .header-badge {{
        color: {VERDE};
        background: rgba(53, 211, 154, 0.12);
        border: 1px solid rgba(53, 211, 154, 0.35);
        border-radius: 6px;
        padding: 6px 14px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
        display: inline-block;
    }}

    .header-badge-cyan {{
        color: {CELESTE};
        background: rgba(32, 196, 232, 0.12);
        border: 1px solid rgba(32, 196, 232, 0.35);
        border-radius: 6px;
        padding: 6px 14px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
        display: inline-block;
    }}

    /* Contenedor del panel de filtros */
    .filter-panel {{
        background-color: {PANEL};
        border: 1px solid {BORDE};
        border-radius: 12px;
        padding: 16px 20px 10px 20px;
        margin-bottom: 1.2rem;
    }}

    .filter-label {{
        color: {SECUNDARIO};
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 4px;
        letter-spacing: 0.4px;
    }}

    /* Estilización de selectores */
    [data-baseweb="select"] > div {{
        background-color: #1a2942 !important;
        border: 1px solid {BORDE} !important;
        border-radius: 8px !important;
        color: {TEXTO} !important;
    }}

    [data-baseweb="select"] * {{
        color: {TEXTO} !important;
    }}

    /* Tarjetas KPI */
    .kpi-card {{
        background-color: {PANEL};
        border: 1px solid {BORDE};
        border-radius: 12px;
        padding: 16px 18px;
        min-height: 105px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }}

    .kpi-card:hover {{
        border-color: #3b5278;
        transform: translateY(-2px);
    }}

    .kpi-title {{
        color: {SECUNDARIO};
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }}

    .kpi-value {{
        font-size: 26px;
        font-weight: 800;
        line-height: 1.1;
    }}

    .kpi-sub {{
        color: {SECUNDARIO};
        font-size: 11px;
        margin-top: 4px;
    }}

    /* Pestañas de navegación (Tabs) */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: transparent;
        gap: 8px;
        border-bottom: 1px solid {BORDE};
        padding-bottom: 4px;
        margin-bottom: 1rem;
    }}

    .stTabs [data-baseweb="tab"] {{
        background-color: {PANEL};
        border: 1px solid {BORDE};
        border-radius: 8px 8px 0px 0px;
        color: {SECUNDARIO};
        font-weight: 700;
        font-size: 13.5px;
        padding: 10px 22px;
    }}

    .stTabs [data-baseweb="tab"]:hover {{
        color: {TEXTO};
        background-color: #1f304d;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: #213554 !important;
        border-color: {CELESTE} !important;
        color: {CELESTE} !important;
    }}

    /* Paneles contenedores */
    .chart-panel {{
        background-color: {PANEL};
        border: 1px solid {BORDE};
        border-radius: 12px;
        padding: 14px 16px 10px 16px;
        margin-bottom: 1rem;
    }}

    .chart-title {{
        color: {TEXTO};
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 4px;
    }}

    .chart-subtitle {{
        color: {SECUNDARIO};
        font-size: 11.5px;
        margin-bottom: 8px;
    }}

    /* Alerta informativa */
    .info-box {{
        background-color: rgba(32, 196, 232, 0.08);
        border: 1px solid rgba(32, 196, 232, 0.25);
        border-radius: 10px;
        padding: 12px 16px;
        font-size: 12px;
        color: {TEXTO};
        margin-bottom: 1rem;
    }}

    /* Pie de página */
    .footer-text {{
        color: {SECUNDARIO};
        font-size: 11px;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid {BORDE};
        text-align: center;
    }}
</style>
"""
