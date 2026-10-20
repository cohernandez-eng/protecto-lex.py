"""Un TOKEN es la unidad mínima que produce el lexer.

Ejemplo: Token(tipo='PR_ENTERO', valor='entero', linea=1)
  - tipo:  la categoría (palabra reservada, número, identificador...)
  - valor: el texto exacto que se leyó del código (el lexema)
  - linea: dónde apareció, para poder reportar errores
"""
from dataclasses import dataclass


@dataclass
class Token:
    tipo: str
    valor: str
    linea: int
