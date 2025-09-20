import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# ===============================
# 1. Cargar y procesar datos
# ===============================
@st.cache_data
def load_data():
    df = pd.read_excel("precios_gasolina_grande.xlsx")
    
    # Renombrar columnas para evitar acentos
    df.rename(columns={
        "estado": "estado",
        "año": "anio",
        "mes": "mes",
        "tipo_combustible": "tipo_combustible",
        "precio": "precio"
    }, inplace=True)
    
    # Asegurar tipos correctos
    df["estado"] = df["estado"].astype(str)
    df["tipo_combustible"] = df["tipo_combustible"].astype(str)
    df["anio"] = df["anio"].astype(int)
    df["mes"] = df["mes"].astype(int)
    
    return df

datos = load_data()

if datos.empty:
    st.error("No se encontraron datos válidos para entrenar el modelo.")
    st.stop()

# ===============================
# 2. Preparar modelo
# ===============================
X = pd.get_dummies(datos[["estado", "anio", "mes", "tipo_combustible"]], drop_first=True)
y = datos["precio"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)

# ===============================
# 3. Interfaz Streamlit
# ===============================
st.title("⛽ Predicción de Precios de Gasolina en México")
st.write("Modelo de regresión lineal múltiple basado en estado, año, mes y tipo de combustible.")

# Entradas del usuario
estado = st.selectbox("Selecciona un estado:", sorted(datos["estado"].unique()))
anio = st.selectbox("Selecciona un año:", sorted(datos["anio"].unique()))
mes = st.selectbox("Selecciona un mes:", list(range(1,13)))
tipo = st.selectbox("Selecciona tipo de combustible:", datos["tipo_combustible"].unique())

# Construir input para predicción
input_df = pd.DataFrame([[estado, anio, mes, tipo]], columns=["estado", "anio", "mes", "tipo_combustible"])
input_encoded = pd.get_dummies(input_df, drop_first=True).reindex(columns=X.columns, fill_value=0)

# Predicción
if st.button("Predecir precio"):
    pred = model.predict(input_encoded)[0]
    st.success(f"💰 Precio estimado: ${pred:.2f} MXN por litro")

# ===============================
# 4. Visualización
# ===============================
st.subheader("Histórico de precios del combustible seleccionado")

df_plot = datos[(datos["estado"]==estado) & (datos["tipo_combustible"]==tipo)].copy()
if df_plot.empty:
    st.write("No hay datos para mostrar en la interfaz.")
else:
    df_plot["fecha"] = pd.to_datetime(df_plot[["anio","mes"]].assign(day=1))
    df_plot = df_plot.sort_values("fecha")

    st.line_chart(df_plot.set_index("fecha")["precio"])

