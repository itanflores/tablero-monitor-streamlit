import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
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

# 💫 Generar Datos de Estado
total_counts = df_filtrado["Estado del Sistema"].value_counts().reset_index()
total_counts.columns = ["Estado", "Cantidad"]

df_grouped = df_filtrado.groupby(["Fecha", "Estado del Sistema"]).size().reset_index(name="Cantidad")
df_grouped["Cantidad_Suavizada"] = df_grouped.groupby("Estado del Sistema")["Cantidad"].transform(lambda x: x.rolling(7, min_periods=1).mean())

df_avg = df_filtrado.groupby("Estado del Sistema")[["Uso CPU (%)", "Memoria Utilizada (%)", "Carga de Red (MB/s)"]].mean().reset_index()

# 📊 Mostrar Gráficos con Mejor Distribución
g1, g2 = st.columns(2)
with g1:
    st.plotly_chart(px.pie(total_counts, values="Cantidad", names="Estado", title="📊 Distribución de Estados", color_discrete_sequence=px.colors.qualitative.Set1), use_container_width=True)
    st.markdown("**Interpretación:** Este gráfico muestra la distribución de estados del sistema en porcentajes, permitiendo identificar la proporción de cada estado.")
    
    st.plotly_chart(px.bar(df_avg, x="Estado del Sistema", y=["Uso CPU (%)", "Memoria Utilizada (%)", "Carga de Red (MB/s)"], barmode="group", title="📊 Uso de Recursos", color_discrete_sequence=px.colors.qualitative.Set3), use_container_width=True)
    st.markdown("**Interpretación:** Comparación del uso promedio de CPU, memoria y carga de red según el estado del sistema, permitiendo evaluar diferencias en consumo de recursos.")

with g2:
    st.plotly_chart(px.line(df_grouped, x="Fecha", y="Cantidad_Suavizada", color="Estado del Sistema", title="📈 Evolución en el Tiempo", markers=True, color_discrete_sequence=px.colors.qualitative.Set2), use_container_width=True)
    st.markdown("**Interpretación:** Representa la evolución temporal de cada estado del sistema, permitiendo detectar tendencias y fluctuaciones a lo largo del tiempo.")
    
    st.plotly_chart(px.box(df_filtrado, x="Estado del Sistema", y="Latencia Red (ms)", color="Estado del Sistema", title="📉 Distribución de la Latencia", color_discrete_sequence=px.colors.qualitative.Set1), use_container_width=True)
    st.markdown("**Interpretación:** Muestra la distribución de la latencia de red para cada estado del sistema, permitiendo identificar valores atípicos y dispersión de los datos.")

# 🔥 Indicador de Predicción de Fallas (Simulación con Tendencia Lineal)
df_grouped['Predicción'] = df_grouped.groupby("Estado del Sistema")["Cantidad_Suavizada"].transform(lambda x: x.shift(-1))
g3, g4 = st.columns(2)
with g3:
    st.plotly_chart(px.line(df_grouped, x="Fecha", y=["Cantidad_Suavizada", "Predicción"], color="Estado del Sistema", title="📈 Predicción de Estados del Sistema", markers=True), use_container_width=True)
    st.markdown("**Interpretación:** Permite visualizar una estimación de la evolución futura de los estados del sistema basada en datos históricos.")

# 🔥 Matriz de Correlación
correlation_matrix = df_filtrado[["Uso CPU (%)", "Memoria Utilizada (%)", "Carga de Red (MB/s)"]].corr()
fig_corr, ax = plt.subplots(figsize=(6, 4))  # Ajuste de tamaño
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
ax.set_title("🔍 Matriz de Correlación entre Variables")
with g4:
    st.pyplot(fig_corr)
    st.markdown("**Interpretación:** Muestra la relación entre las variables de uso de CPU, memoria y carga de red, permitiendo identificar posibles dependencias entre ellas.")

st.success("✅ El tablero ha sido actualizado con explicaciones debajo de cada gráfico.")
