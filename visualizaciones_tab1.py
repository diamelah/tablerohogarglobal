import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
import plotly.express as px

def mostrar_tabla_general(df):
    st.subheader("📊 Análisis General")

    total_encuestas = len(df)
    verbatim_col = "Q2 - ¿Cuál es el motivo de tu calificación?"

    if verbatim_col in df.columns:
        verbatims_validos = df[verbatim_col].dropna()
        verbatims_validos = verbatims_validos[~verbatims_validos.str.strip().isin(["", "-", "--", "---", " ", ".", "…"])]
        total_verbatims = len(verbatims_validos)
        verbatims_vacios = total_encuestas - total_verbatims

        col1, col2, col3 = st.columns(3)
        col1.metric("Q. Encuestas (total)", total_encuestas)
        col2.metric("Q. Verbatims (con contenido)", total_verbatims)
        col3.metric("Q. Verbatims Vacíos", verbatims_vacios)

    grupo_col = None
    for col in df.columns:
        if col.strip().lower().replace(" ", "_") == "grupo_nps":
            grupo_col = col
            break

    st.divider()

    if grupo_col:
        st.subheader("📈 Distribución de Grupo NPS")

        grupo_nps_raw = df[grupo_col].value_counts(normalize=False)
        total = grupo_nps_raw.sum()
        prom = round(grupo_nps_raw.get("Promotor", 0) / total * 100, 1)
        pasivo = round(grupo_nps_raw.get("Pasivo", 0) / total * 100, 1)
        detr = round(grupo_nps_raw.get("Detractor", 0) / total * 100, 1)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'''
<div style='background-color:#8BC34A;padding:10px 5px;border-radius:16px;color:white;text-align:center; margin-bottom:30px;'>
    <div style='font-size:28px;'>&#128522; {prom:.2f}%</div>
    <div><strong>Promotores</strong></div>
</div>
''', unsafe_allow_html=True)

        with col2:
            st.markdown(f'''
<div style='background-color:#FFEB3B;padding:10px 5px;border-radius:16px;color:#333;text-align:center; margin-bottom:30px;'>
    <div style='font-size:28px;'>&#128528; {pasivo:.2f}%</div>
    <div><strong>Pasivos</strong></div>
</div>
''', unsafe_allow_html=True)

        with col3:
            st.markdown(f'''
<div style='background-color:#F44336;padding:10px 5px;border-radius:16px;color:white;text-align:center; margin-bottom:30px;'>
    <div style='font-size:28px;'>&#9785; {detr:.2f}%</div>
    <div><strong>Detractores</strong></div>
</div>
''', unsafe_allow_html=True)

    st.divider()

    causa_raiz_col = "Q3 - ¿Cuál fue el factor que más influyó en tu nota?"

    if causa_raiz_col in df.columns:
        causas = df[causa_raiz_col].dropna()
        causas = causas[~causas.str.strip().isin(["", "-", "--"])]

        if not causas.empty:
            causas_freq = causas.value_counts(normalize=True).round(2) * 100
            causas_freq = causas_freq.sort_values(ascending=False)

            st.subheader("📌 Q.1er Causa Raíz vs. Grupo NPS")

            if grupo_col:
                df_temp = df[[causa_raiz_col, grupo_col]].copy()
                df_temp[causa_raiz_col] = df_temp[causa_raiz_col].fillna("VACIO")
                df_temp[grupo_col] = df_temp[grupo_col].fillna("VACIO")

                pivot = df_temp.value_counts(normalize=False).reset_index(name="Cantidad")
                if not pivot.empty:
                    pivot_table = pivot.pivot_table(
                        index=causa_raiz_col,
                        columns=grupo_col,
                        values="Cantidad",
                        fill_value=0
                    )
                    pivot_table["Total"] = pivot_table.sum(axis=1)
                    if "VACIO" not in pivot_table.columns:
                        pivot_table["VACIO"] = 0
                    cols_order = ["Promotor", "Pasivo", "Detractor", "VACIO", "Total"]
                    pivot_final = pivot_table.reindex(columns=[c for c in cols_order if c in pivot_table.columns])
                    st.dataframe(pivot_final.sort_values("Total", ascending=False))
                else:
                    st.warning("No hay datos suficientes para mostrar la cantidad por causa raíz.")
        else:
            st.info("No hay datos disponibles para mostrar la causa raíz.")

        
        st.divider()
    
    # 🔹 Filtro TÁCTICO aplicado
    tactico_col = "TACTICO"
    grupo_col = "Grupo NPS"

    tactico_filtrado = df[tactico_col].dropna().unique() if tactico_col in df.columns else []

    # 🔹 Si NO hay un único TACTICO seleccionado, mostrar el gráfico de % TÁCTICO por Mes
    if tactico_col in df.columns and "solo_fecha" in df.columns and len(tactico_filtrado) != 1:
        st.subheader("📌 % TÁCTICO por Mes")

        df_tactico = df[[tactico_col, "solo_fecha"]].copy()
        df_tactico[tactico_col] = df_tactico[tactico_col].astype(str).str.strip()
        df_tactico[tactico_col] = df_tactico[tactico_col].replace(["", "-", "--", "---", "nan", "None"], "VACIO")
        df_tactico = df_tactico.dropna(subset=["solo_fecha"])
        df_tactico["mes"] = pd.to_datetime(df_tactico["solo_fecha"]).dt.to_period("M").astype(str)

        agrupado = df_tactico.groupby(["mes", tactico_col]).size().reset_index(name="Cantidad")
        total_por_mes = agrupado.groupby("mes")["Cantidad"].transform("sum")
        agrupado["Porcentaje"] = round((agrupado["Cantidad"] / total_por_mes) * 100, 2)

        pivot = agrupado.pivot(index="mes", columns=tactico_col, values="Porcentaje").fillna(0)
        st.dataframe(pivot)

        try:
            import plotly.express as px
            fig = px.bar(
                agrupado,
                x="mes",
                y="Porcentaje",
                color=tactico_col,
                barmode="group",
                text="Porcentaje",
                title="% TÁCTICO por Mes",
                height=500
            )
            fig.update_traces(texttemplate="%{text}%", textposition="outside")
            fig.update_layout(xaxis_title="Mes", yaxis_title="Porcentaje", legend_title="TÁCTICO")
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            st.warning("Plotly no está disponible para el gráfico interactivo.")

    # 🔹 Si hay un solo valor de TÁCTICO seleccionado, mostrar distribución de NPS
    if tactico_col in df.columns and grupo_col in df.columns and len(tactico_filtrado) == 1:
        tactico_seleccionado = tactico_filtrado[0]
        st.subheader(f"🧩 Distribución de Grupo NPS para TÁCTICO = `{tactico_seleccionado}`")

        df_filtrado_tactico = df[df[tactico_col] == tactico_seleccionado]

        if not df_filtrado_tactico.empty:
            conteo_nps = df_filtrado_tactico[grupo_col].value_counts(normalize=True) * 100
            df_nps = conteo_nps.reset_index()
            df_nps.columns = ["Grupo NPS", "Porcentaje"]

            # ✅ Esto es lo que faltaba
            import plotly.express as px

            fig = px.bar(
                df_nps,
                x="Grupo NPS",
                y="Porcentaje",
                color="Grupo NPS",
                text="Porcentaje",
                color_discrete_map={
                    "Promotor": "#8BC34A",
                    "Pasivo": "#FFEB3B",
                    "Detractor": "#F44336"
                },
                title=f"% de Grupo NPS para '{tactico_seleccionado}'",
                height=500
            )
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig.update_layout(yaxis_title="Porcentaje", xaxis_title="Grupo NPS")
            st.plotly_chart(fig, use_container_width=True)


