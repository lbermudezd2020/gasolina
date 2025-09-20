import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

# ===============================
# 1. Cargar datos
# ===============================
@st.cache_data
def load_data():
    df = pd.read_excel("precios_gasolina_grande.xlsx")
    df["estado"] = df["estado"].astype(str)
    df["tipo_combustible"] = df["tipo_combustible"].astype(str)
    return df

datos = load_data()

if datos.empty:
    st.error("No hay datos disponibles. Revisa tu Excel.")
    st.stop()

# ===============================
# 2. Preparar modelo
# ===============================
X = datos[["estado", "año", "mes", "tipo_combustible"]]
y = datos["precio"]

X_encoded = pd.get_dummies(X, drop_first=True)
model = LinearRegression()
model.fit(X_encoded, y)

# ===============================
# 3. Interfaz Streamlit
# ===============================
st.title("⛽ Predicción de Precios de Gasolina en México")
st.write("Modelo de regresión lineal múltiple basado en estado, año, mes y tipo de combustible.")

# Selección múltiple de estados
estados = st.multiselect("Selecciona uno o más estados:", sorted(datos["estado"].unique()), default=[datos["estado"].unique()[0]])
mes = st.selectbox("Selecciona un mes:", sorted(datos["mes"].unique()))
año = st.selectbox("Selecciona un año:", sorted(datos["año"].unique()))
tipo = st.selectbox("Selecciona tipo de combustible:", sorted(datos["tipo_combustible"].unique()))

# Botón de predicción
if st.button("Predecir precios"):
    resultados = []
    
    for estado in estados:
        # Input
        input_df = pd.DataFrame([[estado, año, mes, tipo]], columns=["estado", "año", "mes", "tipo_combustible"])
        input_encoded = pd.get_dummies(input_df, drop_first=True).reindex(columns=X_encoded.columns, fill_value=0)
        pred = model.predict(input_encoded)[0]
        resultados.append({"estado": estado, "precio_estimado": pred})
    
    # Mostrar resultados
    st.subheader("💰 Precios estimados por estado")
    df_result = pd.DataFrame(resultados)
    st.dataframe(df_result)
    
    # Visualización histórica
    st.subheader("📈 Tendencias históricas")
    for estado in estados:
        df_plot = datos[(datos["estado"]==estado) & (datos["tipo_combustible"]==tipo)]
        df_plot = df_plot.sort_values(by=["año","mes"])
        df_plot["fecha"] = pd.to_datetime(df_plot[["año","mes"]].assign(day=1))
        st.write(f"**{estado} - {tipo}**")
        st.line_chart(df_plot.set_index("fecha")["precio"])
    
    # Promedio nacional por mes
    st.subheader("🌎 Promedio nacional por mes")
    df_avg = datos[(datos["tipo_combustible"]==tipo)].groupby(["año","mes"])["precio"].mean().reset_index()
    df_avg["fecha"] = pd.to_datetime(df_avg[["año","mes"]].assign(day=1))
    st.line_chart(df_avg.set_index("fecha")["precio"])
