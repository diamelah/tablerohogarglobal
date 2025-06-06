import streamlit as st
from data_loader import cargar_datos
from filtros_sidebar import aplicar_filtros
from visualizaciones_tab1 import mostrar_tabla_general
from visualizaciones_tab2 import mostrar_tabla_verbatims, mostrar_tabla_dolores_no_detectados
from visualizaciones_tab3 import mostrar_tabla_contacto
from dolor_detector import detectar_dolor
from utils import normalizar_texto

st.set_page_config(page_title="Dashboard NPS Global", layout="wide")
st.title("📊 Dashboard NPS Global Hogar")

uploaded_file = st.sidebar.file_uploader("📁 Subí tu archivo Excel", type=["xlsx"])

# Inicializar el estado de la pestaña seleccionada
if "tab_index" not in st.session_state:
    st.session_state.tab_index = 0

tab_labels = ["📋 NPS Global Hogar", "🔧 Análisis de Verbatims", "📞 Análisis Dolor en el Contacto"]

if uploaded_file is not None:
    try:
        # 1) Cargo el DataFrame completo
        df = cargar_datos(uploaded_file)

        # 2) Si no existe la columna "Dolor", la creo a partir de Q2 usando detectar_dolor
        razón_col = "Q2 - ¿Cuál es el motivo de tu calificación?"
        if "Dolor" not in df.columns and razón_col in df.columns:
            df["Dolor"] = df[razón_col].fillna("").astype(str).apply(detectar_dolor)

        # 3) Aplico filtros (esto guarda st.session_state["seleccion_grupo"] dentro)
        df_filtrado = aplicar_filtros(df)

        # 4) Selección de pestaña con control de índice en session_state
        selected_tab = st.selectbox("🔽 Elegí una vista", tab_labels, index=st.session_state.tab_index)
        st.session_state.tab_index = tab_labels.index(selected_tab)

        # 5) Mostrar la pestaña correspondiente
        if selected_tab == "📋 NPS Global Hogar":
            mostrar_tabla_general(df_filtrado)

        elif selected_tab == "🔧 Análisis de Verbatims":
            mostrar_tabla_verbatims(df_filtrado)
            mostrar_tabla_dolores_no_detectados(df_filtrado)

        elif selected_tab == "📞 Análisis Dolor en el Contacto":
            mostrar_tabla_contacto(df_filtrado)

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
else:
    st.info("📂 Subí un archivo Excel (.xlsx) para comenzar.")
