"""Lexer propio (Entrega 1) + tokens de expansión del catálogo personal.

Autor: Celso Otoniel Hernández - Carné 2400455

El orden del esquema importa: las expresiones regulares se prueban de arriba
hacia abajo, por eso los comentarios van antes de OP_ARIT ('/'), las palabras
reservadas antes de ID, NUMERO_DECIMAL antes de NUMERO y OP_REL antes de
ASIGNACION.
"""
import re
from typing import List
from .token import Token


def _reservada(palabra: str) -> str:
    return rf'\b{palabra}\b'


class Lexer:

    def __init__(self, codigo_fuente: str):

        self.codigo = codigo_fuente
        self.tokens: List[Token] = []

        self.esquema_tokens = [
                # ---------- Comentarios (se descartan) ----------
                ('COMENTARIO_BLOQUE', r'/\*[\s\S]*?\*/'),
                ('COMENTARIO_LINEA',  r'//[^\n]*'),

                # ---------- Literales de expansión ----------
                ('CADENA_LITERAL',    r'"[^"\n]*"'),
                ('NUMERO_DECIMAL',    r'\d+\.\d+'),

                # ---------- Palabras reservadas base (Entrega 1) ----------
                ('PR_ENTERO',         _reservada('entero')),
                ('PR_SI',             _reservada('si')),
                ('PR_MIENTRAS',       _reservada('mientras')),
                ('PR_IMPRIMIR',       _reservada('imprimir')),

                # ---------- Palabras reservadas de expansión ----------
                ('PR_CADENA',         _reservada('cadena')),
                ('PR_DECIMAL',        _reservada('decimal')),
                ('PR_BOOLEANO',       _reservada('booleano')),
                ('PR_SINO',           _reservada('sino')),
                ('PR_ENTONCES',       _reservada('entonces')),
                ('PR_PARAR',          _reservada('parar')),
                ('PR_CONTINUAR',      _reservada('continuar')),
                ('PR_FUNCION',        _reservada('funcion')),
                ('PR_RETORNAR',       _reservada('retornar')),
                ('PR_LEER',           _reservada('leer')),
                ('BOOLEANO',          r'\b(?:verdadero|falso)\b'),
                ('OP_LOGICO_Y',       _reservada('y')),
                ('OP_LOGICO_O',       _reservada('o')),
                ('OP_LOGICO_NO',      _reservada('no')),

                # ---------- Números e identificadores ----------
                ('NUMERO',            r'\d+'),
                ('ID',                r'[a-zA-Z_][a-zA-Z0-9_]*'),

                # ---------- Operadores ----------
                ('OP_REL',            r'==|!=|<=|>=|<|>'),
                ('OP_ARIT',           r'[+\-*/]'),
                ('ASIGNACION',        r'='),

                # La coma se agrega a DELIM para separar parámetros y
                # argumentos de las funciones (PR_FUNCION).
                ('DELIM',             r'[();{},]'),

                ('ESPACIO',           r'[ \t]+'),
                ('NUEVA_LINEA',       r'\r\n|\n|\r'),
                ('ERROR',             r'.'),
        ]

        self.regex_maestro = re.compile(
            '|'.join(
                f'(?P<{nombre}>{patron})'
                for nombre, patron in self.esquema_tokens
            )
        )

    def analizar(self) -> List[Token]:

        self.tokens = []
        numero_linea = 1

        for match in self.regex_maestro.finditer(self.codigo):

            tipo = match.lastgroup
            valor = match.group()

            if tipo == 'NUEVA_LINEA':
                numero_linea += 1

            elif tipo == 'ESPACIO':
                continue

            elif tipo in ('COMENTARIO_LINEA', 'COMENTARIO_BLOQUE'):
                # Los comentarios no generan tokens, pero un comentario de
                # bloque puede ocupar varias líneas.
                numero_linea += valor.count('\n')

            elif tipo == 'ERROR':
                raise RuntimeError(
                    f"[Error Lexico] "
                    f"Caracter inesperado '{valor}' "
                    f"en linea {numero_linea}"
                )

            else:
                self.tokens.append(Token(tipo, valor, numero_linea))

        self.tokens.append(Token('EOF', '', numero_linea))
        return self.tokens
