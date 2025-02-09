import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar los datasets
df_infraestructura = pd.read_csv("dataset_procesado.csv")
df_modelo = pd.read_csv("dataset_monitoreo_servers.csv")

# Limpiar nombres de columnas
df_infraestructura.columns = df_infraestructura.columns.str.strip()
df_modelo.columns = df_modelo.columns.str.strip()

# Configurar la interfaz del tablero
st.set_page_config(page_title="Tablero de Monitoreo", layout="wide")
st.title("📊 Tablero de Monitoreo del Sistema")

# Crear pestañas
tab1, tab2 = st.tabs(["Infraestructura", "Modelo"])

with tab1:
    st.header("📌 Indicadores de Monitoreo de Infraestructura")
    
    # KPIs principales
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Crítico", df_infraestructura[df_infraestructura["Estado del Sistema"] == "Crítico"].shape[0])
    col2.metric("Advertencia", df_infraestructura[df_infraestructura["Estado del Sistema"] == "Advertencia"].shape[0])
    col3.metric("Normal", df_infraestructura[df_infraestructura["Estado del Sistema"] == "Normal"].shape[0])
    col4.metric("Inactivo", df_infraestructura[df_infraestructura["Estado del Sistema"] == "Inactivo"].shape[0])
    
    # Gráfico de distribución de estados
    fig_estado = px.pie(df_infraestructura, names="Estado del Sistema", title="Distribución de Estados")
    st.plotly_chart(fig_estado, use_container_width=True)
    
    # Gráfico de uso de recursos
    fig_recursos = px.bar(df_infraestructura, x="Estado del Sistema", y=["Uso CPU (%)", "Memoria Utilizada (%)", "Carga de Red (MB/s)"], barmode="group", title="Uso de Recursos por Estado")
    st.plotly_chart(fig_recursos, use_container_width=True)

with tab2:
    st.header("📌 Análisis del Modelo Predictivo")
    
    # Visualización del rendimiento del modelo
    if "Precisión Modelo" in df_modelo.columns:
        st.subheader("📈 Precisión del Modelo")
        fig_precision = px.histogram(df_modelo, x="Precisión Modelo", title="Distribución de Precisión del Modelo")
        st.plotly_chart(fig_precision, use_container_width=True)
    
    # Comparación de eficiencia si existe
    if "Eficiencia Comparativa" in df_modelo.columns:
        st.subheader("📊 Comparativa de Eficiencia")
        fig_eficiencia = px.box(df_modelo, y="Eficiencia Comparativa", title="Distribución de la Eficiencia del Modelo")
        st.plotly_chart(fig_eficiencia, use_container_width=True)
    
    # Relación entre métricas clave
    if "Uso CPU (%)" in df_modelo.columns and "Temperatura (°C)" in df_modelo.columns:
        st.subheader("📉 Relación Uso de CPU vs Temperatura")
        fig_correlation = px.scatter(df_modelo, x="Uso CPU (%)", y="Temperatura (°C)", color="Estado del Sistema", title="Relación entre Uso de CPU y Temperatura")
        st.plotly_chart(fig_correlation, use_container_width=True)
