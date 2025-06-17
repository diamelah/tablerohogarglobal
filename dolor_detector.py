import re
import unicodedata

ORDEN_PRIORIDAD = [
    "Maltrato",
    "Facturación",
    "Precio",
    "IVR",
    "Atención al Cliente",
    "Flow/App",
    "Funcionamiento del Servicio",
    "Velocidad",
    "Instalación",
    "Contenido",
    "Equipos",
    "Sin Dolor Detectado"
]

def normalizar_texto(texto):
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
    texto = re.sub(r'[^\w\s]', '', texto)
    return texto.strip()

def detectar_dolor(verbatim, dolores_dict):
    if not isinstance(verbatim, str) or not verbatim.strip():
        return "Sin Dolor Detectado", "", ""

    texto_norm = normalizar_texto(verbatim)
    encontrados = []

    for dolor, frases in dolores_dict.items():
        for frase in frases:
            if frase in texto_norm:
                encontrados.append(dolor)
                break

    if not encontrados:
        return "Sin Dolor Detectado", "", ""

    ordenados = sorted(encontrados, key=lambda d: ORDEN_PRIORIDAD.index(d) if d in ORDEN_PRIORIDAD else 999)
    principal = ordenados[0]
    secundarios = " + ".join(ordenados[1:]) if len(ordenados) > 1 else ""
    return principal, secundarios, ", ".join(ordenados)
