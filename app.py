import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc

# Cargar datasets
df_infra = pd.read_csv("dataset_procesado.csv")
df_modelo = pd.read_csv("dataset_monitoreo_servers.csv")

# Convertir fechas
df_infra['Fecha'] = pd.to_datetime(df_infra['Fecha'])
df_modelo['Fecha'] = pd.to_datetime(df_modelo['Fecha'])

# Configurar tablero
st.set_page_config(page_title="Tablero de Monitoreo", layout="wide")
st.title("📊 Tablero de Monitoreo del Sistema")

# Crear pestañas
tabs = st.tabs(["Infraestructura", "Modelo"])

### Pestaña 1: Infraestructura
with tabs[0]:
    st.header("🔧 Infraestructura - Estado de los Servidores")
    
    # KPIs principales
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Crítico", df_infra[df_infra["Estado del Sistema"] == "Crítico"].shape[0])
    col2.metric("Advertencia", df_infra[df_infra["Estado del Sistema"] == "Advertencia"].shape[0])
    col3.metric("Normal", df_infra[df_infra["Estado del Sistema"] == "Normal"].shape[0])
    col4.metric("Inactivo", df_infra[df_infra["Estado del Sistema"] == "Inactivo"].shape[0])
    
    # Gráficos
    fig_pie = px.pie(df_infra, names="Estado del Sistema", title="Distribución de Estados")
    fig_line = px.line(df_infra, x="Fecha", y="Uso CPU (%)", color="Estado del Sistema", title="Evolución del Uso de CPU")
    
    st.plotly_chart(fig_pie, use_container_width=True)
    st.plotly_chart(fig_line, use_container_width=True)

### Pestaña 2: Modelo
with tabs[1]:
    st.header("📈 Evaluación del Modelo Predictivo")
    
    # Métricas del modelo
    y_real = df_modelo['Etiqueta Real']
    y_pred = df_modelo['Predicción Modelo']
    cm = confusion_matrix(y_real, y_pred)
    report = classification_report(y_real, y_pred, output_dict=True)
    
    # Gráfico de Matriz de Confusión
    fig, ax = plt.subplots()
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=set(y_real), yticklabels=set(y_real))
    plt.xlabel("Predicción")
    plt.ylabel("Real")
    plt.title("Matriz de Confusión")
    st.pyplot(fig)
    
    # Mostrar reporte
    st.text("Reporte de Clasificación:")
    st.json(report)
    
    # Curva ROC
    fpr, tpr, _ = roc_curve(y_real, y_pred)
    roc_auc = auc(fpr, tpr)
    fig_roc = px.area(x=fpr, y=tpr, title=f"Curva ROC (AUC = {roc_auc:.2f})", labels=dict(x='FPR', y='TPR'))
    st.plotly_chart(fig_roc, use_container_width=True)
    
st.success("✅ Tablero cargado correctamente")
