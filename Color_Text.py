'''
Uso color_name = ROJO, text = "Texto a colorear"
Colores disponibles
Color	Código
Negro	30
Rojo	31
Verde	32
Amarillo	33
Azul	34
Magenta	35
Cian	36
Blanco	37
Gris claro	90
Rojo claro	91
Verde claro	92
Amarillo claro	93
Azul claro	94

'''

ROJO = 31
VERDE = 32
AMARILLO = 33
AZUL = 34
MAGENTA = 35
CIAN = 36
BLANCO = 37
GRIS_CLARO = 90
ROJO_CLARO = 91
VERDE_CLARO = 92
AMARILLO_CLARO = 93
AZUL_CLARO = 94 

def color_text(text, color_name):
    return f"\033[{color_name}m{text}\033[0m"
