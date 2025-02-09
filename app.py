import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
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

# 📊 Mostrar Gráficos
g1, g2 = st.columns(2)
with g1:
    st.plotly_chart(px.pie(total_counts, values="Cantidad", names="Estado", title="📊 Distribución de Estados"), use_container_width=True)
    st.plotly_chart(px.bar(df_avg, x="Estado del Sistema", y=["Uso CPU (%)", "Memoria Utilizada (%)", "Carga de Red (MB/s)"], barmode="group", title="📊 Uso de Recursos"), use_container_width=True)

with g2:
    st.plotly_chart(px.line(df_grouped, x="Fecha", y="Cantidad_Suavizada", color="Estado del Sistema", title="📈 Evolución en el Tiempo", markers=True), use_container_width=True)
    st.plotly_chart(px.box(df_filtrado, x="Estado del Sistema", y="Latencia Red (ms)", color="Estado del Sistema", title="📉 Distribución de la Latencia"), use_container_width=True)

# 📊 Predicción de Estados con Regresión Lineal
pred_horizonte = 12  # Número de meses a predecir
predicciones = []

for estado in df_grouped["Estado del Sistema"].unique():
    df_estado = df_grouped[df_grouped["Estado del Sistema"] == estado].copy()
    df_estado = df_estado.dropna(subset=["Cantidad_Suavizada"])  # Eliminar NaNs
    
    if len(df_estado) > 1:
        X = np.array(range(len(df_estado))).reshape(-1, 1)
        y = df_estado["Cantidad_Suavizada"].values
        model = LinearRegression()
        model.fit(X, y)
        
        future_dates = pd.date_range(start=df_estado["Fecha"].max(), periods=pred_horizonte, freq="M")
        X_future = np.array(range(len(df_estado), len(df_estado) + pred_horizonte)).reshape(-1, 1)
        y_pred = model.predict(X_future)
        
        df_pred = pd.DataFrame({
            "Fecha": future_dates,
            "Estado del Sistema": estado,
            "Cantidad_Suavizada": y_pred
        })
        predicciones.append(df_pred)

df_pred_final = pd.concat([df_grouped] + predicciones, ignore_index=True)
st.plotly_chart(px.line(df_pred_final, x="Fecha", y="Cantidad_Suavizada", color="Estado del Sistema", title="📈 Predicción de Estados del Sistema", markers=True), use_container_width=True)

# 🔥 Matriz de Correlación
correlation_matrix = df_filtrado[["Uso CPU (%)", "Memoria Utilizada (%)", "Carga de Red (MB/s)"]].corr()
fig_corr, ax = plt.subplots(figsize=(5, 3))
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
ax.set_title("🔍 Matriz de Correlación entre Variables")
st.pyplot(fig_corr)
