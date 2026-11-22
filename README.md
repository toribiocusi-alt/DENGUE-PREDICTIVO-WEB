# 🇵🇪 Plataforma Web de Vigilancia y Predicción de Dengue en el Perú

Plataforma web interactiva desarrollada con **Python**, **Streamlit** y **Plotly** para la exploración territorial de la vigilancia epidemiológica y la evaluación de modelos de **Machine Learning** en la predicción semanal de casos de dengue por distrito en el Perú (2025).

---

## 📌 Contexto Epidemiológico y del Modelo

- **Unidad geográfica:** Distrito (código UBIGEO de 6 dígitos normalizado).
- **Unidad temporal:** Semanas epidemiológicas (SE 1 a SE 52 del año 2025).
- **Variable objetivo:** Cantidad de casos notificados de dengue.
- **Horizonte experimental:** 
  - Entrenamiento y ajuste: 2000 – 2023.
  - Validación temporal: 2024.
  - Evaluación retrospectiva: Año 2025 (432 distritos endémicos, 52 semanas).

### 🏆 Modelo Campeón (Benchmark 2025)

| Puesto | Algoritmo | MAE (Casos) | RMSE | WAPE (%) | Rol / Destacado |
|:---:|:---|:---:|:---:|:---:|:---|
| **1** | **LightGBM** | **2.308** | **5.999** | **39.74%** | **Candidato Líder (Mejor MAE y WAPE)** |
| **2** | **Extra Trees** | 2.333 | **5.756** | 40.16% | Mejor RMSE (Precisión en picos) |
| **3** | **Random Forest** | 2.372 | 5.793 | 40.83% | Tercer puesto ensemble |
| 4 | XGBoost | 2.434 | 8.793 | 41.89% | Modelo de gradiente alternativo |
| 5 | Gradient Boosting | 2.493 | 5.834 | 42.92% | Baseline de ensamble |

> ⚠️ **Nota metodológica:** Las métricas mostradas corresponden a una evaluación experimental retrospectiva del año 2025 y deben interpretarse con criterio epidemiológico, no como garantías absolutas de certeza futura.

---

## 🚀 Características de la Plataforma

### 1. Pestaña de Vigilancia y Predicción Epidemiológica
- **Filtros en cascada:** Departamento ➡️ Provincia ➡️ Distrito ➡️ Año (2025) ➡️ Semana Epidemiológica (Todas o SE 1-52) ➡️ Algoritmo (16 modelos disponibles).
- **Tarjetas KPI dinámicas:** 
  - Casos Reales
  - Predicción ML
  - Error Absoluto Medio (MAE puntual para el ámbito y semana seleccionados)
  - WAPE (%)
  - RMSE
  - Semana de Mayor Incidencia (Pico anual)
- **Gráfico 1: Evolución Semanal mediante Líneas (Plotly):**
  - Muestra la serie continua de **todas las semanas epidemiológicas de 2025 (SE 1 a SE 52)**.
  - Dos series: Casos Reales y Casos Predichos, con anotación del pico epidemiológico.
  - El filtro de semana **no recorta este gráfico**, conservando la perspectiva anual completa.
- **Gráfico 2: Comparación mediante Barras (Plotly):**
  - Compara Casos Reales vs. Casos Predichos.
  - Con "Todas las semanas": compara el acumulado anual de todas las semanas disponibles.
  - Con una semana específica: compara puntualmente esa semana epidemiológica.
- **Distribución de Casos (Curva Epidémica):**
  - Visualización del volumen semanal de casos con leyenda descriptiva transparente.

### 2. Pestaña de Comparación de Algoritmos (Benchmark)
- Tabla completa de los 16 modelos evaluados ordenada por MAE.
- Gráficos comparativos interactivos de barras horizontales (MAE, WAPE %, RMSE).
- Selector interactivo para aplicar cualquier modelo directamente al dashboard principal.

---

## 📁 Estructura del Proyecto

```
DENGUE-PREDICTIVO-WEB/
├── .streamlit/
│   └── config.toml               # Configuración del tema oscuro oficial
├── data/
│   ├── catalogo_ubigeos.csv      # Catálogo ligero de correspondencia geográfica (25 KB)
│   ├── comparacion_algoritmos_dengue_2025.csv # Resultados del benchmark experimental (1.2 KB)
│   └── predicciones_2025_*.csv   # Archivos de predicción de los 16 modelos (~4.5 MB total)
├── src/
│   ├── __init__.py
│   ├── config.py                 # Paleta visual, rutas y estilos CSS
│   ├── data_loader.py            # Carga y caché con @st.cache_data
│   ├── data_processor.py         # Filtrado en cascada y cálculo de KPIs
│   └── plots.py                  # Generación de figuras interactivas Plotly
├── app.py                        # Punto de entrada de la aplicación Streamlit
├── requirements.txt              # Dependencias de Python
├── tests_web.py                  # Suite de 11 pruebas unitarias automatizadas
├── .gitignore                    # Reglas de exclusión de Git
└── README.md                     # Documentación general y guía de despliegue
```

---

## 💻 Instalación y Ejecución Local

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/toribiocusi-alt/DENGUE-PREDICTIVO-WEB.git
   cd DENGUE-PREDICTIVO-WEB
   ```

2. **Crear y activar entorno virtual (opcional pero recomendado):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Linux/Mac
   # .venv\Scripts\activate   # En Windows
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar pruebas unitarias:**
   ```bash
   python tests_web.py
   ```

5. **Iniciar la aplicación web:**
   ```bash
   streamlit run app.py
   ```
   La aplicación se abrirá en `http://localhost:8501`.

---

## ☁️ Guía de Publicación en Streamlit Community Cloud

Para que tus compañeros y docentes puedan acceder públicamente desde cualquier navegador:

### Paso 1: Subir el repositorio a GitHub

> 💡 **Recomendación clave:** Se recomienda crear el repositorio como **Público** (`Public`) para que Streamlit Community Cloud tenga acceso inmediato sin requerir configuración adicional de permisos OAuth en organizaciones o cuentas personales.

Desde la carpeta del proyecto:
```bash
cd ~/Descargas/DENGUE-PREDICTIVO-WEB
git init
git add .
git commit -m "feat: plataforma web de prediccion de dengue con streamlit y plotly"
git branch -M main
git remote add origin https://github.com/toribiocusi-alt/DENGUE-PREDICTIVO-WEB.git
git push -u origin main
```

*(Si utilizas GitHub CLI ya autenticado: `gh repo create toribiocusi-alt/DENGUE-PREDICTIVO-WEB --public --source=. --push`)*

### Paso 2: Desplegar en Streamlit Cloud

1. Ingresa a **[share.streamlit.io](https://share.streamlit.io/)** e inicia sesión con tu cuenta de GitHub (`toribiocusi-alt`).
2. Haz clic en el botón **"Create app"** (o **"New app"**).
3. Selecciona la opción **"I have an app"** y completa los campos:
   - **Repository:** `toribiocusi-alt/DENGUE-PREDICTIVO-WEB`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL (opcional):** `dengue-peru-prediccion` (o el subdominio que elijas)
4. Haz clic en **"Deploy!"**.
5. En unos segundos, Streamlit instalará las dependencias de `requirements.txt` y tu aplicación estará disponible globalmente en:
   **`https://dengue-peru-prediccion.streamlit.app/`**
