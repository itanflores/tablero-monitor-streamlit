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
def create_card(title, fig):
    st.markdown(f"""
        <div class='card'>
            <h3>{title}</h3>
        </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)

fig_pie = px.pie(total_counts, values="Cantidad", names="Estado", title="📊 Distribución de Estados", color_discrete_sequence=px.colors.qualitative.Set1)
fig_line = px.line(df_grouped, x="Fecha", y="Cantidad_Suavizada", color="Estado del Sistema", title="📈 Evolución en el Tiempo", markers=True, color_discrete_sequence=px.colors.qualitative.Set2)
fig_bar = px.bar(df_avg, x="Estado del Sistema", y=["Uso CPU (%)", "Memoria Utilizada (%)", "Carga de Red (MB/s)"], barmode="group", title="📊 Uso de Recursos", color_discrete_sequence=px.colors.qualitative.Set3)
fig_boxplot = px.box(df_filtrado, x="Estado del Sistema", y="Latencia Red (ms)", color="Estado del Sistema", title="📉 Distribución de la Latencia", color_discrete_sequence=px.colors.qualitative.Set1)
fig_trend = px.scatter(df_filtrado.melt(id_vars=["Fecha"], value_vars=["Uso CPU (%)", "Memoria Utilizada (%)", "Carga de Red (MB/s)"], var_name="Variable", value_name="Valor"), x="Fecha", y="Valor", color="Variable", title="📊 Tendencia de Uso de Recursos", color_discrete_sequence=px.colors.qualitative.Set2)

# 🔦 Manejo seguro de las métricas para evitar errores de índice
def get_estado_count(estado):
    return total_counts.loc[total_counts["Estado"] == estado, "Cantidad"].values[0] if estado in total_counts["Estado"].values else 0

# 📌 Diseño Mejorado
st.markdown("""
    <style>
        .title-container {
            text-align: center;
            font-size: 2em;
            font-weight: bold;
        }
        .metric-container {
            display: flex;
            justify-content: space-around;
            gap: 15px;
        }
        .stButton>button {
            background-color: #FF4B4B;
            color: white;
        }
        .card {
            background-color: #1E1E1E;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(255, 255, 255, 0.2);
            margin-bottom: 10px;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
        h3 {
            color: white;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title-container'>📊 Tablero de Monitoreo del Sistema</div>", unsafe_allow_html=True)
st.subheader("📌 KPIs del Sistema")

# 📊 Mostrar métricas clave con mejor diseño
g1, g2, g3, g4 = st.columns(4)
with g1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.metric("Crítico", get_estado_count("Crítico"))
    st.markdown("</div>", unsafe_allow_html=True)
with g2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.metric("Advertencia", get_estado_count("Advertencia"))
    st.markdown("</div>", unsafe_allow_html=True)
with g3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.metric("Normal", get_estado_count("Normal"))
    st.markdown("</div>", unsafe_allow_html=True)
with g4:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.metric("Inactivo", get_estado_count("Inactivo"))
    st.markdown("</div>", unsafe_allow_html=True)

# 📊 Mostrar Gráficos en Layout Mejorado con Marcos
g1, g2 = st.columns(2)
with g1:
    create_card("📊 Distribución de Estados", fig_pie)
with g2:
    create_card("📈 Evolución en el Tiempo", fig_line)

g3, g4 = st.columns(2)
with g3:
    create_card("📊 Uso de Recursos", fig_bar)
with g4:
    create_card("📉 Distribución de la Latencia", fig_boxplot)

create_card("📊 Tendencia de Uso de Recursos", fig_trend)

st.success("✅ El tablero está listo y funcionando en Streamlit Cloud.")
