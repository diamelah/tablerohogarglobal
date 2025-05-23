from dolores_keywords import dolores
from utils import normalizar_texto
import re

# Separar array de frases "Indefinido"
frases_indefinido = dolores.get("Indefinido", [])
dolores_filtrados = {k: v for k, v in dolores.items() if k != "Indefinido"}

def contiene_clave_flexible(frase_cliente, clave_normalizada):
    """
    Devuelve True si:
    - clave_normalizada está como frase completa
    - o todas sus palabras aparecen por separado (en cualquier orden)
    - o es una palabra única y aparece como palabra exacta
    """
    if " " in clave_normalizada:
        if clave_normalizada in frase_cliente:
            return True
        palabras_clave = clave_normalizada.split()
        return all(p in frase_cliente for p in palabras_clave)
    else:
        return bool(re.search(rf"\b{re.escape(clave_normalizada)}\b", frase_cliente))

def detectar_dolor(verbatim):
    if not isinstance(verbatim, str) or not verbatim.strip():
        return "Sin Dolor Detectado"

    if not re.search(r"\b[a-zA-Z]{3,}\b", verbatim):
        return "Sin Dolor Detectado"

    frase_cliente = normalizar_texto(verbatim)

    # 1️⃣ Intentar clasificar en cualquier dolor definido
    for dolor, frases in dolores_filtrados.items():
        for frase_clave in frases:
            clave_normalizada = normalizar_texto(frase_clave)
            if contiene_clave_flexible(frase_cliente, clave_normalizada):
                return dolor

    # 2️⃣ Si no matcheó ningún dolor, revisar si encaja como Indefinido
    for frase_indef in frases_indefinido:
        clave_normalizada = normalizar_texto(frase_indef)
        if contiene_clave_flexible(frase_cliente, clave_normalizada):
            return "Indefinido"

    # 3️⃣ Si no se encontró ni como dolor ni como indefinido
    return "Sin Dolor Detectado"
