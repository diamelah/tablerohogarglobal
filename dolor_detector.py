# dolor_detector.py

from dolores_keywords import dolores
from utils import normalizar_texto, expandir_sinonimos
import re
from rapidfuzz import fuzz  # Para fuzzy matching

# Extraemos las frases de “Indefinido” y creamos un dict sin esa categoría
dolores_filtrados = {k: v for k, v in dolores.items() if k != "Indefinido"}
frases_indefinido = dolores.get("Indefinido", [])


def contiene_clave_flexible(frase_cliente: str, clave_normalizada: str) -> bool:
    """
    - Si clave_normalizada tiene más de una palabra, chequea que todas aparezcan en frase_cliente.
    - Si es una sola palabra, busca con word-boundaries (\b...\b) para evitar empates parciales.
    """
    if " " in clave_normalizada:
        if clave_normalizada in frase_cliente:
            return True
        tokens = clave_normalizada.split()
        return all(tok in frase_cliente for tok in tokens)
    else:
        return bool(re.search(rf"\b{re.escape(clave_normalizada)}\b", frase_cliente))


def detectar_dolor(verbatim: str) -> str:
    """
    1) Si no es string válido, o está vacío, o no contiene al menos 3 letras seguidas => "Sin Dolor Detectado"
    2) Normaliza el texto (quita acentos/puntuación/stopwords).
    3) Expande sinónimos (por ej. “valor” -> “precio”, “factura” -> “facturacion”).
    4) Recorre todas las categorías (excepto "Indefinido") en busca de coincidencia exacta; si la encuentra, devuelve la categoría.
    5) Si no hubo match exacto, recorre las frases de "Indefinido" (solo aquellas que no normalicen a vacío)
       y, si coincide, devuelve "Indefinido".
    6) Si sigue sin match, aplica fuzzy matching para encontrar la categoría más parecida.
    7) Si ninguna similitud supera el umbral, devuelve "Sin Dolor Detectado".
    """
    # 1) Validación rápida
    if not isinstance(verbatim, str) or not verbatim.strip():
        return "Sin Dolor Detectado"
    if not re.search(r"\b[a-zA-Z]{3,}\b", verbatim):
        return "Sin Dolor Detectado"

    # 2) Normalizar y 3) Expandir sinónimos
    frase_cliente = normalizar_texto(verbatim)
    frase_cliente = expandir_sinonimos(frase_cliente)

    # 4) Matching exacto en todas las categorías (sin "Indefinido")
    for categoria, lista_frases in dolores_filtrados.items():
        for frase_clave in lista_frases:
            clave_norm = normalizar_texto(frase_clave)
            if not clave_norm:
                continue
            if contiene_clave_flexible(frase_cliente, clave_norm):
                return categoria

    # 5) Matching exacto en "Indefinido"
    for frase_indef in frases_indefinido:
        clave_norm = normalizar_texto(frase_indef)
        if not clave_norm:
            continue
        if contiene_clave_flexible(frase_cliente, clave_norm):
            return "Indefinido"

    # 6) Fuzzy matching fallback
    mejor_categoria = None
    mejor_ratio = 0
    UMBRAL_FUZZY = 80  # Ajustar entre 70-90 según tolerancia deseada

    for categoria, lista_frases in dolores_filtrados.items():
        for frase_clave in lista_frases:
            clave_norm = normalizar_texto(frase_clave)
            if not clave_norm:
                continue
            ratio = fuzz.partial_ratio(frase_cliente, clave_norm)
            if ratio > mejor_ratio:
                mejor_ratio = ratio
                mejor_categoria = categoria

    if mejor_ratio >= UMBRAL_FUZZY:
        return mejor_categoria

    # 7) Si nada coincide
    return "Sin Dolor Detectado"
