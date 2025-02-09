import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 💞 Cargar Dataset
DATASET_URL = "dataset_procesado.csv"
if not os.path.exists(DATASET_URL):
    st.error("❌ Error: El dataset no se encuentra en la ruta especificada.")
    st.stop()

df = pd.read_csv(DATASET_URL)
df.columns = df.columns.str.strip()
df['Fecha'] = pd.to_datetime(df['Fecha'])

# 📌 Filtros
fecha_min, fecha_max = df["Fecha"].min(), df["Fecha"].max()
fecha_seleccionada = st.date_input("Selecciona un rango de fechas:", [fecha_min.date(), fecha_max.date()], fecha_min.date(), fecha_max.date())
fecha_seleccionada = [pd.to_datetime(fecha) for fecha in fecha_seleccionada]
df = df[(df["Fecha"] >= fecha_seleccionada[0]) & (df["Fecha"] <= fecha_seleccionada[1])]

estados_seleccionados = st.multiselect("Selecciona uno o más Estados:", df["Estado del Sistema"].unique(), default=df["Estado del Sistema"].unique())
df = df[df["Estado del Sistema"].isin(estados_seleccionados)]

cpu_min, cpu_max = st.slider("Filtrar Uso CPU (%)", int(df["Uso CPU (%)"].min()), int(df["Uso CPU (%)"].max()), (int(df["Uso CPU (%)"].min()), int(df["Uso CPU (%)"].max())))
df = df[(df["Uso CPU (%)"] >= cpu_min) & (df["Uso CPU (%)"] <= cpu_max)]

if st.button("Restablecer Filtros"):
    st.experimental_rerun()

# 📊 Generar Datos de Estado
total_counts = df["Estado del Sistema"].value_counts().reset_index()
total_counts.columns = ["Estado", "Cantidad"]

df_grouped = df.groupby(["Fecha", "Estado del Sistema"]).size().reset_index(name="Cantidad")
df_grouped["Cantidad_Suavizada"] = df_grouped.groupby("Estado del Sistema")["Cantidad"].transform(lambda x: x.rolling(7, min_periods=1).mean())

df_avg = df.groupby("Estado del Sistema")[["Uso CPU (%)", "Memoria Utilizada (%)", "Carga de Red (MB/s)"]].mean().reset_index()

# 🎨 Crear Gráficos con Datos Filtrados
fig_pie = px.pie(total_counts, values="Cantidad", names="Estado", title="📊 Distribución de Estados")
fig_line = px.line(df_grouped, x="Fecha", y="Cantidad_Suavizada", color="Estado del Sistema", title="📈 Evolución en el Tiempo", markers=True)
fig_bar = px.bar(df_avg, x="Estado del Sistema", y=["Uso CPU (%)", "Memoria Utilizada (%)", "Carga de Red (MB/s)"], barmode="group", title="📊 Uso de Recursos")
fig_boxplot = px.box(df, x="Estado del Sistema", y="Latencia Red (ms)", color="Estado del Sistema", title="📉 Distribución de la Latencia")

# 🔦 Manejo seguro de las métricas para evitar errores de índice
def get_estado_count(estado):
    return total_counts.loc[total_counts["Estado"] == estado, "Cantidad"].values[0] if estado in total_counts["Estado"].values else 0

# 🖥️ Configurar Interfaz en Streamlit
st.set_page_config(page_title="Tablero de Monitoreo", page_icon="📊", layout="wide")

st.title("📊 Tablero de Monitoreo del Sistema")
st.subheader("📌 KPIs del Sistema")

# 📊 Mostrar métricas clave con manejo de errores
col1, col2, col3, col4 = st.columns(4)
col1.metric("Crítico", get_estado_count("Crítico"))
col2.metric("Advertencia", get_estado_count("Advertencia"))
col3.metric("Normal", get_estado_count("Normal"))
col4.metric("Inactivo", get_estado_count("Inactivo"))

# 📊 Mostrar Gráficos
st.plotly_chart(fig_pie, use_container_width=True)
st.plotly_chart(fig_line, use_container_width=True)
st.plotly_chart(fig_bar, use_container_width=True)
st.plotly_chart(fig_boxplot, use_container_width=True)

st.success("✅ El tablero está listo y funcionando en Streamlit Cloud.")
