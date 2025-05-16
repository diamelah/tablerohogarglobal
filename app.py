import streamlit as st
from data_loader import cargar_datos
from filtros_sidebar import aplicar_filtros
from visualizaciones_tab1 import mostrar_tabla_general
from visualizaciones_tab2 import mostrar_tabla_verbatims
from visualizaciones_tab3 import mostrar_tabla_contacto
from dolor_detector import detectar_dolor
from utils import normalizar_texto

st.set_page_config(page_title="Dashboard NPS Global", layout="wide")
st.title("📊 Dashboard NPS Global - Hogar")

uploaded_file = st.sidebar.file_uploader("📁 Subí tu archivo Excel", type=["xlsx"])

# Inicializar el estado de la pestaña seleccionada
if "tab_index" not in st.session_state:
    st.session_state.tab_index = 0

tab_labels = ["📋 General", "🔧Análisis Verbatims", "📞 Análisis de Contacto de Clientes"]

if uploaded_file is not None:
    try:
        df = cargar_datos(uploaded_file)

        if "Dolor" not in df.columns and "Q2 - ¿Cuál es el motivo de tu calificación?" in df.columns:
            df["Dolor"] = df["Q2 - ¿Cuál es el motivo de tu calificación?"].apply(detectar_dolor)

        df_filtrado = aplicar_filtros(df)

        # Renderizar tabs con control de selección
        selected_tab = st.selectbox("🔽 Elegí una vista", tab_labels, index=st.session_state.tab_index)

        # Actualizar el índice de pestaña en session_state
        st.session_state.tab_index = tab_labels.index(selected_tab)

        # Mostrar la pestaña correspondiente
        if selected_tab == "📋 General":
            mostrar_tabla_general(df_filtrado)
        elif selected_tab == "🔧Análisis Verbatims":
            mostrar_tabla_verbatims(df_filtrado)
        elif selected_tab == "📞 Análisis de Contacto de Clientes":
            mostrar_tabla_contacto(df_filtrado)

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
else:
    st.info("📂 Subí un archivo Excel (.xlsx) para comenzar.")
