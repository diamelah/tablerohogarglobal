import streamlit as st
import pandas as pd
import io

@st.cache_data
def cargar_datos(archivo_excel):
    # Leer el Excel una sola vez
    df = pd.read_excel(archivo_excel, engine="openpyxl")

    # Convertir a CSV en memoria
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    # Leer el CSV como si fuera una nueva carga, más liviana.-
    df_csv = pd.read_csv(buffer)

    # Convertir fecha si existe
    if 'Fecha' in df_csv.columns:
        df_csv['Fecha'] = pd.to_datetime(df_csv['Fecha'], errors='coerce')

    return df_csv
