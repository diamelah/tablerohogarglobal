import unicodedata
import re
from dolores_keywords import dolores

# 🔄 Diccionario de sinónimos
sinonimos = {
    "facturacion": ["factura", "boleta", "cobro"],
    "precio": ["valor", "costo"],
    "servicio": ["atencion", "soporte", "ayuda"],
    "tecnico": ["tecnica", "tecnologia"],
    "pago": ["abono", "deposito"],
    "cliente": ["usuario", "abonado"]
}

# 🧹 Palabras que se eliminan (stopwords/conectores)
conectores = {'que', 'y', 'pero', 'porque', 'por', 'para', 'con', 'sin', 'de', 'la', 'el', 'en', 'lo', 'a', 'un', 'una', 'al', 'del'}

def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""

    texto = texto.lower()
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    texto = re.sub(r'[^\w\s]', ' ', texto)  # eliminar signos de puntuación
    palabras = texto.split()
    palabras_filtradas = [p for p in palabras if p not in conectores]
    return ' '.join(palabras_filtradas).strip()

def expandir_sinonimos(frase):
    for clave, lista in sinonimos.items():
        for sinonimo in lista:
            frase = re.sub(rf"\b{re.escape(sinonimo)}\b", clave, frase)
    return frase

# Separar frases de "Indefinido"
frases_indefinido = dolores.get("Indefinido", [])
dolores_filtrados = {k: v for k, v in dolores.items() if k != "Indefinido"}

def contiene_clave_flexible(frase_cliente, clave_normalizada):
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
    frase_cliente = expandir_sinonimos(frase_cliente)

    for dolor, frases in dolores_filtrados.items():
        for frase_clave in frases:
            clave_normalizada = normalizar_texto(frase_clave)
            if contiene_clave_flexible(frase_cliente, clave_normalizada):
                return dolor

    for frase_indef in frases_indefinido:
        clave_normalizada = normalizar_texto(frase_indef)
        if contiene_clave_flexible(frase_cliente, clave_normalizada):
            return "Indefinido"

    return "Sin Dolor Detectado"
