from dolor_detector import detectar_dolor
import pandas as pd
from utils import normalizar_texto
import streamlit as st
import io  # 👈 necesario para exportar

def mostrar_tabla_verbatims(df):
    st.subheader("📝 Tabla de Verbatims - 1er Causa Raíz")
    st.markdown("ℹ️ En dicha tabla podemos usar los filtros en el menú izquierdo y luego exportar el análisis como archivo **.xlsx**.")

    if df.empty:
        st.warning("⚠️ No hay datos disponibles con los filtros aplicados.")
        return

    if "Q2_normalizado" not in df.columns and "Q2 - ¿Cuál es el motivo de tu calificación?" in df.columns:
        df["Q2_normalizado"] = df["Q2 - ¿Cuál es el motivo de tu calificación?"].apply(normalizar_texto)
    if "Q15_normalizado" not in df.columns and "Q15_2_TEXT - No, ¿por qué?" in df.columns:
        df["Q15_normalizado"] = df["Q15_2_TEXT - No, ¿por qué?"].apply(normalizar_texto)

    if "Dolor" not in df.columns:
        df["Texto_combinado"] = df["Q2_normalizado"].fillna("") + " " + df["Q15_normalizado"].fillna("")
        df["Dolor"] = df["Texto_combinado"].apply(detectar_dolor)

    st.subheader("🔍 Búsqueda personalizada")

    palabras_input = st.text_input("Buscar palabras clave (separadas por coma)", "")
    palabras = [normalizar_texto(p.strip()) for p in palabras_input.split(",") if p.strip()]

    if palabras:
        def contiene_palabras(texto):
            texto = normalizar_texto(str(texto))
            return any(palabra in texto for palabra in palabras)

        df = df[
            df["Q2 - ¿Cuál es el motivo de tu calificación?"].astype(str).apply(contiene_palabras)
            | df["Q15_2_TEXT - No, ¿por qué?"].astype(str).apply(contiene_palabras)
        ]

    dolores_disponibles = sorted(df["Dolor"].dropna().unique())
    filtro_dolor = st.selectbox("Filtrar por Dolor", ["Todos"] + dolores_disponibles)

    if filtro_dolor != "Todos":
        df = df[df["Dolor"] == filtro_dolor]
        
    # 🕓 Mostrar solo la fecha sin hora
    if "Fecha de finalización (+00:00 GMT)" in df.columns:
        df["Fecha"] = pd.to_datetime(df["Fecha de finalización (+00:00 GMT)"], errors="coerce").dt.date
        
    # 🪪 Renombrar la columna de documento para visualización y exportación
        df = df.rename(columns={"PERSONA_DOCUMENTO_NUMERO": "DNI"})

    st.markdown("### 🧩 Seleccionar columnas adicionales (Q4 a Q8)")
    columnas_extra = {
        "Q4 - Servicio": "Q4- ¿Cuál de estas opciones influyó más en tu elección? SERVICIO",
        "Q5 - Precio": "Q5-¿Cuál de estas opciones influyó más en tu elección? PRECIO",
        "Q6 - Atención al Cliente": "Q6-¿Cuál de estas opciones influyó más en tu elección?-ATEN. CLIENTES",
        "Q7 - Servicio Técnico": "Q7-¿Cuál de estas opciones influyó más en tu elección?-- SERV. TECN.",
        "Q8 - Facturación y Pago": "Q8-¿Cuál de estas opciones influyó más en tu elección?-FACT. Y PAGO"
    }

    columnas_seleccionadas = [col for label, col in columnas_extra.items() if st.checkbox(label, value=False, key=label)]

    columnas_base = [
        "Fecha",
        "DNI",
        "Grupo NPS",
        "NPS",
        "Dolor",
        "Q2 - ¿Cuál es el motivo de tu calificación?",
        "Q3 - ¿Cuál fue el factor que más influyó en tu nota?"
    ]

    columnas = columnas_base + columnas_seleccionadas
    columnas_existentes = [col for col in columnas if col in df.columns]

    if columnas_existentes:
        st.dataframe(df[columnas_existentes])

        # 👇 Exportar como Excel .xlsx*-
        output = io.BytesIO()
        df[columnas_existentes].to_excel(output, index=False, sheet_name="Verbatims")
        output.seek(0)

        st.download_button(
            label="⬇️ Descargar tabla como Excel",
            data=output,
            file_name="verbatims_filtrados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No se encontraron las columnas requeridas para mostrar la tabla de verbatims.")

    st.markdown("### 📅 Dolores por Mes")

    if "Fecha de inicio (+00:00 GMT)" in df.columns and "Dolor" in df.columns:
        df_fechado = df.copy()
        df_fechado["Mes"] = pd.to_datetime(df_fechado["Fecha de inicio (+00:00 GMT)"], errors="coerce").dt.to_period("M").astype(str)
        df_fechado["Dolor"] = df_fechado["Dolor"].fillna("Sin Dolor")

        pivot_dolor = df_fechado.pivot_table(
            index="Dolor",
            columns="Mes",
            values="Q2 - ¿Cuál es el motivo de tu calificación?",
            aggfunc="count",
            fill_value=0
        ).sort_index()

        st.dataframe(pivot_dolor)
    else:
        st.warning("No se puede generar la tabla de Dolores por mes. Falta alguna columna.")
