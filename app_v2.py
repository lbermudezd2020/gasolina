import streamlit as st
import pandas as pd

st.set_page_config(page_title="Predicción de Gasolina México", layout="wide")

st.title("⛽ Predicción de Precios de Gasolina en México")
st.write("""
Esta aplicación estima el precio de la gasolina según estado, mes, año y tipo de combustible.
""")

# ===============================
# 1. Cargar datos
# ===============================
@st.cache_data
def cargar_datos():
    df = pd.read_excel("gasolina_mexico.xlsx")
    df = df.dropna(subset=["estado","anio","mes","tipo_combustible","precio"])
    return df

datos = cargar_datos()

# ===============================
# 2. Menús interactivos
# ===============================
estados = sorted(datos["estado"].unique())
años = sorted(datos["anio"].unique())
meses = sorted(datos["mes"].unique())
tipos_combustible = sorted(datos["tipo_combustible"].unique())

estado = st.selectbox("Selecciona un estado", estados)
año = st.selectbox("Selecciona un año", años)
mes = st.selectbox("Selecciona un mes", meses)
tipo = st.selectbox("Selecciona tipo de combustible", tipos_combustible)

# ===============================
# 3. Predicción (precio promedio histórico)
# ===============================
df_filtro = datos[
    (datos["estado"]==estado) & 
    (datos["anio"]==año) & 
    (datos["mes"]==mes) & 
    (datos["tipo_combustible"]==tipo)
]

if df_filtro.empty:
    st.warning("No hay datos para los filtros seleccionados.")
else:
    precio_estimado = df_filtro["precio"].mean()
    st.success(f"💰 Precio estimado de {tipo} en {estado} ({mes}/{año}): ${precio_estimado:.2f} MXN")

# ===============================
# 4. Visualización histórica
# ===============================
st.subheader("Histórico de precios del combustible seleccionado")

df_plot = datos[(datos["estado"]==estado) & (datos["tipo_combustible"]==tipo)].copy()

if df_plot.empty:
    st.write("No hay datos para mostrar en la gráfica.")
else:
    # Crear columna fecha de forma robusta
    df_plot = df_plot.dropna(subset=["anio","mes","precio"])
    df_plot["fecha"] = pd.to_datetime(dict(year=df_plot["anio"], month=df_plot["mes"], day=1))
    df_plot = df_plot.sort_values("fecha")

    st.line_chart(df_plot.set_index("fecha")["precio"])

# ===============================
# 5. Tabla de datos
# ===============================
st.subheader("Tabla de precios")
st.dataframe(df_plot[["anio","mes","tipo_combustible","precio"]])


