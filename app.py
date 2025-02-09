import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import os
from sklearn.linear_model import LinearRegression
import numpy as np

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

# 📌 KPIs del Sistema
st.subheader("📌 KPIs del Sistema")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Crítico", total_counts.loc[total_counts["Estado"] == "Crítico", "Cantidad"].values[0] if "Crítico" in total_counts["Estado"].values else 0)
kpi2.metric("Advertencia", total_counts.loc[total_counts["Estado"] == "Advertencia", "Cantidad"].values[0] if "Advertencia" in total_counts["Estado"].values else 0)
kpi3.metric("Normal", total_counts.loc[total_counts["Estado"] == "Normal", "Cantidad"].values[0] if "Normal" in total_counts["Estado"].values else 0)
kpi4.metric("Inactivo", total_counts.loc[total_counts["Estado"] == "Inactivo", "Cantidad"].values[0] if "Inactivo" in total_counts["Estado"].values else 0)

df_grouped = df_filtrado.groupby(["Fecha", "Estado del Sistema"]).size().reset_index(name="Cantidad")
df_grouped["Cantidad_Suavizada"] = df_grouped.groupby("Estado del Sistema")["Cantidad"].transform(lambda x: x.rolling(7, min_periods=1).mean())

df_avg = df_filtrado.groupby("Estado del Sistema")[["Uso CPU (%)", "Memoria Utilizada (%)", "Carga de Red (MB/s)"]].mean().reset_index()

# 🔥 Indicador de Predicción de Fallas con Regresión Lineal
future_days = 7
df_pred = df_grouped.copy()
df_pred['Días'] = (df_pred['Fecha'] - df_pred['Fecha'].min()).dt.days

model = LinearRegression()
for estado in df_pred["Estado del Sistema"].unique():
    df_estado = df_pred[df_pred["Estado del Sistema"] == estado]
    if len(df_estado) > 1:
        X = df_estado[["Días"]]
        y = df_estado[["Cantidad_Suavizada"]]
        model.fit(X, y)
        max_days = df_pred["Días"].max()
        if not np.isnan(max_days):
            future_dates = np.array(range(int(max_days) + 1, int(max_days) + 1 + future_days)).reshape(-1, 1)
            future_predictions = model.predict(future_dates)
            future_df = pd.DataFrame({"Fecha": df_pred["Fecha"].max() + pd.to_timedelta(future_dates.flatten(), unit='D'),
                                      "Cantidad_Suavizada": future_predictions.flatten(),
                                      "Estado del Sistema": estado})
            df_pred = pd.concat([df_pred, future_df], ignore_index=True)

# 📊 Gráficas del tablero
g1, g2 = st.columns(2)
with g1:
    st.plotly_chart(px.pie(total_counts, names="Estado", values="Cantidad", title="📊 Distribución de Estados"), use_container_width=True)
    st.markdown("**Interpretación:** Este gráfico muestra la distribución de estados del sistema en porcentajes, permitiendo identificar la proporción de cada estado.")

    st.plotly_chart(px.line(df_grouped, x="Fecha", y="Cantidad_Suavizada", color="Estado del Sistema", title="📈 Evolución en el Tiempo"), use_container_width=True)
    st.markdown("**Interpretación:** Representa la evolución temporal de cada estado del sistema, permitiendo detectar tendencias y fluctuaciones a lo largo del tiempo.")

with g2:
    st.plotly_chart(px.bar(df_avg, x="Estado del Sistema", y=["Uso CPU (%)", "Memoria Utilizada (%)", "Carga de Red (MB/s)"], title="📊 Uso Promedio de Recursos por Estado"), use_container_width=True)
    st.markdown("**Interpretación:** Comparación del uso promedio de CPU, memoria y carga de red según el estado del sistema, permitiendo evaluar diferencias en consumo de recursos.")

    correlation_matrix = df_filtrado[["Uso CPU (%)", "Memoria Utilizada (%)", "Carga de Red (MB/s)"]].corr()
    fig_corr, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
    ax.set_title("🔍 Matriz de Correlación entre Variables")
    st.pyplot(fig_corr)
    st.markdown("**Interpretación:** Muestra la relación entre las variables de uso de CPU, memoria y carga de red, permitiendo identificar posibles dependencias entre ellas.")

st.success("✅ El tablero ha sido actualizado con una predicción más precisa y mejor visualización de todas las métricas y gráficos.")
