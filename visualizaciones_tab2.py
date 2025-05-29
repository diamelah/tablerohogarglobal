from dolor_detector import detectar_dolor
import pandas as pd
from utils import normalizar_texto
import streamlit as st
import io  # 💈 necesario para exportar
import xlsxwriter

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

    # 🧪 Renombrar la columna de documento para visualización y exportación
        df = df.rename(columns={"PERSONA_DOCUMENTO_NUMERO": "DNI"})

    st.markdown("### 🧩 Seleccionar columnas adicionales")

    # Checkbox para incluir el resto de los campos del Excel
    incluir_todos_los_campos = st.checkbox("📦 Incluir el resto de los campos/columnas del .xlsx", value=False)

    # Columnas base que siempre deben estar
    columnas_base = [
        "Fecha",
        "DNI",
        "Grupo NPS",
        "TACTICO",
        "Dolor",
        "Q2 - ¿Cuál es el motivo de tu calificación?",
        "Q3 - ¿Cuál fue el factor que más influyó en tu nota?"
    ]

    if incluir_todos_los_campos:
        columnas = columnas_base + [col for col in df.columns if col not in columnas_base]
    else:
        columnas = columnas_base

    # Filtrar columnas que existen en el DataFrame
    columnas_existentes = [col for col in columnas if col in df.columns]

    if columnas_existentes:
        st.dataframe(df[columnas_existentes])

        # Exportar como Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df[columnas_existentes].to_excel(writer, sheet_name="Verbatims", startrow=3, index=False)
        workbook = writer.book
        worksheet = writer.sheets["Verbatims"]

        # Agregar título en la parte superior
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center',
            'valign': 'vcenter'
        })
        worksheet.merge_range(0, 0, 0, len(columnas_existentes) - 1, 'Análisis de Verbatims', title_format)

        # Agregar autofiltros
        worksheet.autofilter(3, 0, 3 + len(df), len(columnas_existentes) - 1)

    output.seek(0)

    st.download_button(
        label="⬇️ Descargar tabla como Excel",
        data=output,
        file_name="analisis_verbatims.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.markdown("### 📅 Dolores por Mes")

    if "Fecha de finalización (+00:00 GMT)" in df.columns and "Dolor" in df.columns:
        df_fechado = df.copy()
        df_fechado["Mes"] = pd.to_datetime(df_fechado["Fecha de finalización (+00:00 GMT)"], errors="coerce").dt.to_period("M").astype(str)
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

def mostrar_tabla_dolores_no_detectados(df):
    st.markdown("### 📊 Análisis por tipo de Dolor no detectado")

    opciones = ["Indefinido", "Sin Dolor Detectado"]
    opcion_seleccionada = st.radio("Seleccioná el tipo de caso a mostrar:", opciones)

    if "Dolor" in df.columns and "TACTICO" in df.columns and "Grupo NPS" in df.columns:
        df_filtrado = df[df["Dolor"] == opcion_seleccionada]
        if df_filtrado.empty:
            st.info(f"No se encontraron casos con Dolor '{opcion_seleccionada}'.")
        else:
            tabla = df_filtrado.groupby(["TACTICO", "Grupo NPS"]).size().unstack(fill_value=0)
            st.dataframe(tabla, use_container_width=True)

            output = io.BytesIO()
            nombre_hoja = opcion_seleccionada.replace(" ", "_")
            nombre_archivo = f"dolor_{nombre_hoja.lower()}_por_tactico.xlsx"
            tabla.to_excel(output, index=True, sheet_name=nombre_hoja)
            output.seek(0)

            st.download_button(
                label=f"⬇️ Descargar tabla '{opcion_seleccionada}' como Excel",
                data=output,
                file_name=nombre_archivo,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.warning("No se puede generar la tabla. Faltan columnas necesarias.")






    
