# 📌 Tablero de Monitoreo del Sistema en Streamlit
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 📥 Cargar Dataset
DATASET_URL = "dataset_procesado.csv"  # Reemplázalo con una URL pública si es necesario
if not os.path.exists(DATASET_URL):
    st.error("❌ Error: El dataset no se encuentra en la ruta especificada.")
    st.stop()

df = pd.read_csv(DATASET_URL)
df.columns = df.columns.str.strip()
df['Fecha'] = pd.to_datetime(df['Fecha'])

# 📊 Generar Datos de Estado
estado_counts = df["Estado del Sistema"].value_counts().reset_index()
estado_counts.columns = ["Estado", "Cantidad"]

df_grouped = df.groupby(["Fecha", "Estado del Sistema"]).size().reset_index(name="Cantidad")
df_grouped["Cantidad_Suavizada"] = df_grouped.groupby("Estado del Sistema")["Cantidad"].transform(lambda x: x.rolling(7, min_periods=1).mean())

df_avg = df.groupby("Estado del Sistema")[["Uso CPU (%)", "Memoria Utilizada (%)", "Carga de Red (MB/s)"]].mean().reset_index()

# 🎨 Crear Gráficos
fig_pie = px.pie(estado_counts, values="Cantidad", names="Estado", title="📊 Distribución de Estados")
fig_line = px.line(df_grouped, x="Fecha", y="Cantidad_Suavizada", color="Estado del Sistema", title="📈 Evolución en el Tiempo", markers=True)
fig_bar = px.bar(df_avg, x="Estado del Sistema", y=["Uso CPU (%)", "Memoria Utilizada (%)", "Carga de Red (MB/s)"], barmode="group", title="📊 Uso de Recursos")
fig_boxplot = px.box(df, x="Estado del Sistema", y="Latencia Red (ms)", color="Estado del Sistema", title="📉 Distribución de la Latencia")

# 🖥️ Configurar Interfaz en Streamlit
st.set_page_config(page_title="Tablero de Monitoreo", page_icon="📊", layout="wide")

st.title("📊 Tablero de Monitoreo del Sistema")
st.subheader("📌 KPIs del Sistema")

# 📌 Mostrar métricas clave
col1, col2, col3, col4 = st.columns(4)
col1.metric("Crítico", estado_counts.loc[estado_counts["Estado"] == "Crítico", "Cantidad"].values[0])
col2.metric("Advertencia", estado_counts.loc[estado_counts["Estado"] == "Advertencia", "Cantidad"].values[0])
col3.metric("Normal", estado_counts.loc[estado_counts["Estado"] == "Normal", "Cantidad"].values[0])
col4.metric("Inactivo", estado_counts.loc[estado_counts["Estado"] == "Inactivo", "Cantidad"].values[0])

# 📌 Filtros
estado_seleccionado = st.selectbox("Selecciona el Estado del Sistema:", df["Estado del Sistema"].unique())

df_filtrado = df[df["Estado del Sistema"] == estado_seleccionado]
fig_trend = px.scatter(df_filtrado, x="Fecha", y=["Uso CPU (%)", "Memoria Utilizada (%)", "Carga de Red (MB/s)"], title=f"Tendencia de Uso de Recursos - {estado_seleccionado}")

# 📊 Mostrar Gráficos en Pestañas
tabs = st.tabs(["Distribución", "Evolución", "Uso de Recursos", "Latencia", "Tendencia"])
with tabs[0]:
    st.plotly_chart(fig_pie)
with tabs[1]:
    st.plotly_chart(fig_line)
with tabs[2]:
    st.plotly_chart(fig_bar)
with tabs[3]:
    st.plotly_chart(fig_boxplot)
with tabs[4]:
    st.plotly_chart(fig_trend)

# 🔄 Nota: No se necesita Ngrok para Streamlit Cloud

st.success("✅ El tablero está listo y funcionando en Streamlit Cloud.")
