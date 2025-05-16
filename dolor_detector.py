from dolores_keywords import dolores_normalizados
from dolores_keywords import normalizar_frase
from utils import normalizar_texto

def detectar_dolor(verbatim):
    if not isinstance(verbatim, str):
        return "Sin Verbatim"

    frase_normalizada = normalizar_frase(normalizar_texto(verbatim))

    for dolor, frases in dolores_normalizados.items():
        for frase in frases:
            if frase in frase_normalizada:
                return dolor
    return "Sin Dolor Detectado"
