import re
from .token import Token
from typing import List


class Lexer:

    def __init__(self, codigo_fuente: str):

        self.codigo = codigo_fuente
        self.tokens: List[Token] = []

        self.esquema_tokens = [
                # Palabras reservadas (deben ir antes de ID para que no
                # sean interpretadas como identificadores)
                ('PR_ENTERO',   r'\bentero\b'),
                ('PR_SI',       r'\bsi\b'),
                ('PR_MIENTRAS', r'\bmientras\b'),
                ('PR_IMPRIMIR', r'\bimprimir\b'),

                ('NUMERO',      r'\d+'),
                ('ID',          r'[a-zA-Z_][a-zA-Z0-9_]*'),

                # Operadores relacionales (deben ir antes de ASIGNACION
                # para que '==', '!=', '<=' y '>=' no se partan en dos
                # tokens de un solo caracter)
                ('OP_REL',      r'==|!=|<=|>=|<|>'),

                ('OP_ARIT',     r'[+\-*/]'),
                ('ASIGNACION',  r'='),
                ('DELIM',       r'[();{}]'),
                ('ESPACIO',     r'[ \t]+'),
                ('NUEVA_LINEA', r'\n'),
                ('ERROR',       r'.')
        ]

        self.regex_maestro = re.compile(
            '|'.join(
                f'(?P<{nombre}>{patron})'
                for nombre, patron in self.esquema_tokens
            )
        )


    def analizar(self) -> List[Token]:

        numero_linea = 1

        for match in self.regex_maestro.finditer(self.codigo):

            tipo = match.lastgroup
            valor = match.group()

            if tipo == 'NUEVA_LINEA':

                numero_linea += 1

            elif tipo == 'ESPACIO':

                continue

            elif tipo == 'COMENTARIO':

                # Los comentarios no generan tokens
                continue

            elif tipo == 'ERROR':

                raise RuntimeError(
                    f"[Error Lexico] "
                    f"Caracter inesperado '{valor}' "
                    f"en linea {numero_linea}"
                )

            else:

                self.tokens.append(
                    Token(
                        tipo,
                        valor,
                        numero_linea
                    )
                )

        self.tokens.append(
            Token('EOF', '', numero_linea)
        )

        return self.tokens