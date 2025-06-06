# utils.py

import unicodedata
import re

# 🔄 Diccionario de sinónimos (clave -> lista de términos que normalizamos a esa clave)
sinonimos = {
    "facturacion": ["factura", "boleta", "cobro"],
    "precio":      ["valor", "costo"],
    "servicio":    ["atencion", "soporte", "ayuda"],
    "tecnico":     ["tecnica", "tecnologia"],
    "pago":        ["abono", "deposito"],
    "cliente":     ["usuario", "abonado"]
}

# 🧹 Conectores (stopwords) que se eliminan en la normalización
conectores = {
    "que", "y", "pero", "porque", "por", "para", "con",
    "sin", "de", "la", "el", "en", "lo", "a", "un", "una",
    "al", "del"
}


def normalizar_texto(texto: str) -> str:
    """
    1) Pasar a minúsculas.
    2) Quitar tildes/acentos (ASCII básico).
    3) Reemplazar todo lo que no sea letra/dígito por espacio.
    4) Tokenizar y eliminar los conectores.
    5) Devolver la frase resultante unida por espacios.
    """
    if not isinstance(texto, str):
        return ""
    texto = texto.lower()
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    texto = re.sub(r'[^\w\s]', ' ', texto)
    palabras = texto.split()
    palabras_filtradas = [p for p in palabras if p not in conectores]
    return ' '.join(palabras_filtradas).strip()


def expandir_sinonimos(frase: str) -> str:
    """
    Reemplaza en la frase cada sinónimo por su clave.
    Ejemplo: “cobro” -> “facturacion”, “valor” -> “precio”, etc.
    """
    for clave, lista_sins in sinonimos.items():
        for sin in lista_sins:
            frase = re.sub(rf"\b{re.escape(sin)}\b", clave, frase)
    return frase
