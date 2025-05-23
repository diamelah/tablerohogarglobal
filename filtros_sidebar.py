import streamlit as st
import pandas as pd

def aplicar_filtros(df):
    st.sidebar.subheader("📅 Filtro por Fecha")

    if 'Fecha de inicio (+00:00 GMT)' in df.columns:
        df['fecha'] = pd.to_datetime(df['Fecha de inicio (+00:00 GMT)'], errors='coerce')
        df = df.dropna(subset=['fecha'])
        df['solo_fecha'] = df['fecha'].dt.date

        fecha_min = df['solo_fecha'].min()
        fecha_max = df['solo_fecha'].max()

        fecha_inicio = st.sidebar.date_input("Fecha inicio", value=fecha_min, min_value=fecha_min, max_value=fecha_max)
        fecha_fin = st.sidebar.date_input("Fecha fin", value=fecha_max, min_value=fecha_min, max_value=fecha_max)

        df = df[(df['solo_fecha'] >= fecha_inicio) & (df['solo_fecha'] <= fecha_fin)]

    campos_filtrables = [
        'Grupo_NPS',
        'Q.Encuestas',
        'Q.Verbatims',
        'Q.Verbatims Vacios',
        'Q3 - ¿Cuál fue el factor que más influyó en tu nota?',
        'TACTICO',
        'NPS',
        'Grupo NPS',
        'Q4- ¿Cuál de estas opciones influyó más en tu elección? SERVICIO',
        'Q5-¿Cuál de estas opciones influyó más en tu elección? PRECIO',
        'Q6-¿Cuál de estas opciones influyó más en tu elección?-ATEN. CLIENTES',
        'Q7-¿Cuál de estas opciones influyó más en tu elección?-- SERV. TECN.',
        'Q8-¿Cuál de estas opciones influyó más en tu elección?-FACT. Y PAGO',
        'Q14 - En el último mes, ¿Te contactaste con nuestro centro de atención al cliente...',
        'Q15 - ¿Se resolvió el motivo por el cual te contactaste?',
        'Q125- A tráves de que canal te contactaste:',
        'TECNOLOGIA',
        'SCORE',
        'Dolor'
    ]

    for campo in campos_filtrables:
        if campo in df.columns:
            opciones_raw = df[campo].dropna()
            es_numerico = pd.api.types.is_numeric_dtype(df[campo])

            if es_numerico:
                opciones = sorted(set(int(op) for op in opciones_raw if pd.notnull(op)))
                opciones = ["Todos"] + opciones
                seleccion = st.sidebar.selectbox(f"{campo}", opciones, key=campo)
                if seleccion != "Todos":
                    df = df[df[campo] == seleccion]
            else:
                opciones = sorted([str(op) for op in df[campo].fillna("VACIO").unique()])
                opciones = ["Todos"] + opciones
                seleccion = st.sidebar.selectbox(f"{campo}", opciones, key=campo)
                if seleccion != "Todos":
                    df = df[df[campo].fillna("VACIO") == seleccion]

    return df

#actus