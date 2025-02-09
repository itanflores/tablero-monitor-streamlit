import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import os

# 🛠️ Configurar la página antes que cualquier otro comando
st.set_page_config(page_title="Tablero de Monitoreo", page_icon="📊", layout="wide")

# 📢 Título del tablero
st.title("📊 Tablero de Monitoreo del Sistema")

# 💞 Cargar Dataset
DATASET_URL = "dataset_procesado.csv"
if not os.path.exists(DATASET_URL):
    st.error("❌ Error: El dataset no se encuentra en la ruta especificada.")
    st.stop()

df = pd.read_csv(DATASET_URL)
df.columns = df.columns.str.strip()
df['Fecha'] = pd.to_datetime(df['Fecha'])

# 📌 Filtros
estados_seleccionados = st.multiselect("Selecciona uno o más Estados:", df["Estado del Sistema"].unique(), default=df["Estado del Sistema"].unique())
df_filtrado = df[df["Estado del Sistema"].isin(estados_seleccionados)]

# 💫 Generar Datos de Estado
total_counts = df_filtrado["Estado del Sistema"].value_counts().reset_index()
total_counts.columns = ["Estado", "Cantidad"]

df_grouped = df_filtrado.groupby(["Fecha", "Estado del Sistema"]).size().reset_index(name="Cantidad")
df_grouped["Cantidad_Suavizada"] = df_grouped.groupby("Estado del Sistema")["Cantidad"].transform(lambda x: x.rolling(7, min_periods=1).mean())

df_avg = df_filtrado.groupby("Estado del Sistema")[["Uso CPU (%)", "Memoria Utilizada (%)", "Carga de Red (MB/s)"]].mean().reset_index()

# 📌 KPIs del Sistema
st.subheader("📌 KPIs del Sistema")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Crítico", total_counts.loc[total_counts["Estado"] == "Crítico", "Cantidad"].values[0] if "Crítico" in total_counts["Estado"].values else 0)
kpi2.metric("Advertencia", total_counts.loc[total_counts["Estado"] == "Advertencia", "Cantidad"].values[0] if "Advertencia" in total_counts["Estado"].values else 0)
kpi3.metric("Normal", total_counts.loc[total_counts["Estado"] == "Normal", "Cantidad"].values[0] if "Normal" in total_counts["Estado"].values else 0)
kpi4.metric("Inactivo", total_counts.loc[total_counts["Estado"] == "Inactivo", "Cantidad"].values[0] if "Inactivo" in total_counts["Estado"].values else 0)

# 📊 Predicción de Temperatura Crítica
st.subheader("🌡️ Predicción de Temperatura Crítica")

if "Uso CPU (%)" in df_filtrado.columns and "Temperatura (°C)" in df_filtrado.columns:
    df_temp = df_filtrado[["Fecha", "Uso CPU (%)", "Carga de Red (MB/s)", "Temperatura (°C)"]].dropna()
    X = df_temp[["Uso CPU (%)", "Carga de Red (MB/s)"]]
    y = df_temp["Temperatura (°C)"]
    
    model_temp = RandomForestRegressor(n_estimators=100, random_state=42)
    model_temp.fit(X, y)
    
    future_cpu_usage = np.linspace(df_temp["Uso CPU (%)"].min(), df_temp["Uso CPU (%)"].max(), num=12)
    future_network_load = np.linspace(df_temp["Carga de Red (MB/s)"].min(), df_temp["Carga de Red (MB/s)"].max(), num=12)
    future_dates = pd.date_range(start=df_temp["Fecha"].max(), periods=12, freq="M")
    
    future_data = pd.DataFrame({
        "Uso CPU (%)": future_cpu_usage,
        "Carga de Red (MB/s)": future_network_load
    })
    future_temp_pred = model_temp.predict(future_data)
    
    df_future_temp = pd.DataFrame({
        "Fecha": future_dates,
        "Temperatura Predicha (°C)": future_temp_pred
    })
    
    fig_temp = px.line(df_future_temp, x="Fecha", y="Temperatura Predicha (°C)", title="📈 Predicción de Temperatura Crítica", markers=True)
    st.plotly_chart(fig_temp, use_container_width=True)

# 🔥 Matriz de Correlación
g3, _ = st.columns(2)
with g3:
    correlation_matrix = df_filtrado[["Uso CPU (%)", "Memoria Utilizada (%)", "Carga de Red (MB/s)"]].corr()
    fig_corr, ax = plt.subplots(figsize=(4, 2))  # Reducción de tamaño
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
    ax.set_title("🔍 Matriz de Correlación entre Variables")
    st.pyplot(fig_corr)
