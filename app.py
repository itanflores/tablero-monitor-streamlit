import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 🛠️ Configurar la página antes que cualquier otro comando
st.set_page_config(page_title="Tablero de Monitoreo", page_icon="📊", layout="wide")

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

# 💊 Generar Datos de Estado
total_counts = df_filtrado["Estado del Sistema"].value_counts().reset_index()
total_counts.columns = ["Estado", "Cantidad"]

df_grouped = df_filtrado.groupby(["Fecha", "Estado del Sistema"]).size().reset_index(name="Cantidad")
df_grouped["Cantidad_Suavizada"] = df_grouped.groupby("Estado del Sistema")["Cantidad"].transform(lambda x: x.rolling(7, min_periods=1).mean())

df_avg = df_filtrado.groupby("Estado del Sistema")[["Uso CPU (%)", "Memoria Utilizada (%)", "Carga de Red (MB/s)"]].mean().reset_index()

# 🎨 Crear Gráficos con Datos Filtrados
fig_pie = px.pie(total_counts, values="Cantidad", names="Estado", title="📊 Distribución de Estados")
fig_line = px.line(df_grouped, x="Fecha", y="Cantidad_Suavizada", color="Estado del Sistema", title="📈 Evolución en el Tiempo", markers=True)
fig_bar = px.bar(df_avg, x="Estado del Sistema", y=["Uso CPU (%)", "Memoria Utilizada (%)", "Carga de Red (MB/s)"], barmode="group", title="📊 Uso de Recursos")
fig_boxplot = px.box(df_filtrado, x="Estado del Sistema", y="Latencia Red (ms)", color="Estado del Sistema", title="📉 Distribución de la Latencia")
fig_trend = px.scatter(df_filtrado, x="Fecha", y=["Uso CPU (%)", "Memoria Utilizada (%)", "Carga de Red (MB/s)"], title="📊 Tendencia de Uso de Recursos")

# 🔦 Manejo seguro de las métricas para evitar errores de índice
def get_estado_count(estado):
    return total_counts.loc[total_counts["Estado"] == estado, "Cantidad"].values[0] if estado in total_counts["Estado"].values else 0

st.title("📊 Tablero de Monitoreo del Sistema")
st.subheader("📌 KPIs del Sistema")

# 📊 Mostrar métricas clave con manejo de errores
top_row = st.columns(4)
top_row[0].metric("Crítico", get_estado_count("Crítico"))
top_row[1].metric("Advertencia", get_estado_count("Advertencia"))
top_row[2].metric("Normal", get_estado_count("Normal"))
top_row[3].metric("Inactivo", get_estado_count("Inactivo"))

# 📊 Mostrar Gráficos en un diseño más compacto
row1 = st.columns(2)
row1[0].plotly_chart(fig_pie, use_container_width=True)
row1[1].plotly_chart(fig_line, use_container_width=True)

row2 = st.columns(2)
row2[0].plotly_chart(fig_bar, use_container_width=True)
row2[1].plotly_chart(fig_boxplot, use_container_width=True)

st.plotly_chart(fig_trend, use_container_width=True)

st.success("✅ El tablero está listo y funcionando en Streamlit Cloud.")
