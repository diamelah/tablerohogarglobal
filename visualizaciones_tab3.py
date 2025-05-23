import streamlit as st
import pandas as pd
import io

def mostrar_tabla_contacto(df):
    st.subheader("📞 Análisis de Contacto de Clientes")

    if df.empty:
        st.warning("⚠️ No hay datos disponibles con los filtros aplicados.")
        return

    # Asegurar que la fecha sea reconocida
    if "Fecha de inicio (+00:00 GMT)" in df.columns:
        df["fecha"] = pd.to_datetime(df["Fecha de inicio (+00:00 GMT)"], errors="coerce")
        df["solo_fecha"] = df["fecha"].dt.date

    # 🔎 Filtros
    st.markdown("### 🔎 Filtros de análisis")

    if "solo_fecha" in df.columns:
        fecha_max = df["solo_fecha"].max()
        fecha_min = fecha_max - pd.Timedelta(days=30)
        rango_ultimos_30 = st.checkbox("📆 Ver solo contactos de los últimos 30 días", value=False)
        if rango_ultimos_30:
            df = df[(df["solo_fecha"] >= fecha_min) & (df["solo_fecha"] <= fecha_max)]

    contacto_col = "Q14 - En el último mes, ¿Te contactaste con nuestro centro de atención al cliente..."
    canal_col = "Q125- A tráves de que canal te contactaste:"
    resolvio_col = "Q15 - ¿Se resolvió el motivo por el cual te contactaste?"

    # Filtro Q14
    if contacto_col in df.columns:
        opciones_q14 = ["Todos"] + sorted(df[contacto_col].dropna().unique().tolist())
        seleccion_q14 = st.selectbox("📆 ¿Se contactó el último mes?", opciones_q14)
        if seleccion_q14 != "Todos":
            df = df[df[contacto_col] == seleccion_q14]

    # Filtro canal
    if canal_col in df.columns:
        canal_opciones = ["Todos"] + sorted(df[canal_col].dropna().unique().tolist())
        canal_sel = st.selectbox("📨 Canal de contacto", canal_opciones)
        if canal_sel != "Todos":
            df = df[df[canal_col] == canal_sel]

    # Filtro resolución
    if resolvio_col in df.columns:
        res_opciones = ["Todos"] + sorted(df[resolvio_col].dropna().unique().tolist())
        res_sel = st.selectbox("✅ ¿Se resolvió?", res_opciones)
        if res_sel != "Todos":
            df = df[df[resolvio_col] == res_sel]
            
    # Mostrar solo fecha y renombrar columna
    if "Fecha de finalización (+00:00 GMT)" in df.columns:
        df["Fecha"] = pd.to_datetime(df["Fecha de finalización (+00:00 GMT)"], errors="coerce").dt.date

    # ▶ Tabla principal
    st.markdown("### 🗂️ Tabla general filtrada")
    columnas = [
        
        contacto_col,
        canal_col,
        resolvio_col,
        "Q15_2_TEXT - No, ¿por qué?",
        "Fecha"
    ] 
    columnas_existentes = [col for col in columnas if col in df.columns]
    st.dataframe(df[columnas_existentes], use_container_width=True)

    # Exportar tabla general como Excel
    output_general = io.BytesIO()
    with pd.ExcelWriter(output_general, engine='xlsxwriter') as writer:
        df[columnas_existentes].to_excel(writer, index=False, sheet_name="TablaFiltrada")

    st.download_button(
        label="📥 Descargar tabla filtrada como .xlsx",
        data=output_general.getvalue(),
        file_name="tabla_contacto_filtrada.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    


    # ▶ Tabla resumen
    st.markdown("### 📊 Cantidad de respuestas por campo")

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

        # 📥 Exportar como Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_resumen.to_excel(writer, index=False, sheet_name="Resumen")
        st.download_button(
            label="📥 Descargar resumen como .xlsx",
            data=output.getvalue(),
            file_name="resumen_contacto.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No hay datos para mostrar en el resumen de respuestas.")
