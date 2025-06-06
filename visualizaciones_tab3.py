import streamlit as st
import pandas as pd
import io

def mostrar_tabla_contacto(df):
    st.markdown("### 📊 Contacto del Cliente según Dolor")

    if df.empty:
        st.warning("⚠️ No hay datos disponibles con los filtros aplicados.")
        return

    # Filtro por Dolor
    dolor_actual = "Todos"
    if "Dolor" in df.columns:
        dolores_disponibles = sorted(df["Dolor"].dropna().unique().tolist())
        dolor_seleccionado = st.selectbox("🩺 Filtrar por Dolor", ["Todos"] + dolores_disponibles)
        if dolor_seleccionado != "Todos":
            df = df[df["Dolor"] == dolor_seleccionado]
            dolor_actual = dolor_seleccionado

    # Variables de interés
    contacto_col = "Q14 - En el último mes, ¿Te contactaste con nuestro centro de atención al cliente..."
    canal_col = "Q125- A tráves de que canal te contactaste:"
    resolvio_col = "Q15 - ¿Se resolvió el motivo por el cual te contactaste?"

    resumen = []

    if contacto_col in df.columns:
        cuenta_q14 = df[contacto_col].value_counts().reset_index()
        cuenta_q14.columns = ["Respuesta", "Cantidad"]
        cuenta_q14.insert(0, "Campo", "Q14 - ¿Se contactó el último mes?")
        resumen.append(cuenta_q14)

    if canal_col in df.columns:
        cuenta_q125 = df[canal_col].value_counts().reset_index()
        cuenta_q125.columns = ["Respuesta", "Cantidad"]
        cuenta_q125.insert(0, "Campo", "Q125 - Canal de contacto")
        resumen.append(cuenta_q125)

    if resolvio_col in df.columns:
        cuenta_q15 = df[resolvio_col].value_counts().reset_index()
        cuenta_q15.columns = ["Respuesta", "Cantidad"]
        cuenta_q15.insert(0, "Campo", "Q15 - ¿Se resolvió?")
        resumen.append(cuenta_q15)

    if resumen:
        df_resumen = pd.concat(resumen, ignore_index=True)
        st.dataframe(df_resumen)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book
            worksheet = workbook.add_worksheet("Resumen")
            writer.sheets["Resumen"] = worksheet

            # 🔵 Formato del título
            titulo_format = workbook.add_format({
                'bold': True,
                'font_color': 'blue',
                'font_size': 14
            })

            titulo = f"Resumen de Contacto - Dolor: {dolor_actual}"
            worksheet.write(0, 0, titulo, titulo_format)

            # 📊 Escribir los datos a partir de la fila 3
            df_resumen.to_excel(writer, sheet_name="Resumen", startrow=2, index=False)

        st.download_button(
            label="📥 Descargar resumen como .xlsx",
            data=output.getvalue(),
            file_name=f"resumen_contacto_{dolor_actual.lower().replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No hay datos para mostrar en el resumen de respuestas.")

    # ▶ Tabla con respuestas "No, ¿por qué?" y comentario asociado
    st.markdown("### 📋 Motivos cuando la respuesta fue 'No, ¿por qué?'")

    col_resolvio = "Q15 - ¿Se resolvió el motivo por el cual te contactaste?"
    col_comentario = "Q15_2_TEXT - No, ¿por qué?"
    col_fecha = "Fecha de finalización (+00:00 GMT)"

    if col_resolvio in df.columns and col_comentario in df.columns:
        df_filtrado = df[df[col_resolvio].str.strip().str.lower() == "no, ¿por qué?"].copy()
        df_filtrado = df_filtrado[df_filtrado[col_comentario].notna() & df_filtrado[col_comentario].str.strip().ne("")]

        if col_fecha in df.columns:
            df_filtrado["Fecha"] = pd.to_datetime(df[col_fecha], errors="coerce").dt.date

        columnas_mostrar = ["Fecha", col_resolvio, col_comentario]
        columnas_existentes = [c for c in columnas_mostrar if c in df_filtrado.columns]

        if not df_filtrado.empty:
            st.dataframe(df_filtrado[columnas_existentes], use_container_width=True)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_filtrado[columnas_existentes].to_excel(writer, sheet_name="No_Porque", startrow=3, index=False)
                workbook = writer.book
                worksheet = writer.sheets["No_Porque"]

                # Título
                title_format = workbook.add_format({
                    'bold': True,
                    'font_size': 14,
                    'align': 'center',
                    'valign': 'vcenter'
                })
                worksheet.merge_range(0, 0, 0, len(columnas_existentes) - 1, "Análisis de Motivos - No, ¿por qué?", title_format)

                # Autofiltro
                worksheet.autofilter(3, 0, 3 + len(df_filtrado), len(columnas_existentes) - 1)

            output.seek(0)

            st.download_button(
                label="📥 Descargar motivos 'No, ¿por qué?'",
                data=output,
                file_name="motivos_no_porque.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        else:
            st.info("✅ No hay comentarios asociados a respuestas 'No, ¿por qué?'.")
    else:
        st.warning("❗ Faltan columnas necesarias para mostrar los motivos 'No, ¿por qué?'.")
