"""
==========================================================================
 FASE 1 DEL COMPILADOR: ANALIZADOR LÉXICO (LEXER)
==========================================================================
 Autor: Celso Otoniel Hernández - Carné 2400455
 Curso: Compiladores - USPG

 ¿QUÉ HACE ESTE ARCHIVO?
   Recibe el código fuente como un texto cualquiera y lo parte en
   piezas con nombre llamadas TOKENS.

   Ejemplo:   entero edad = 20;
   produce:   Token(PR_ENTERO, 'entero')   Token(ID, 'edad')
              Token(ASIGNACION, '=')       Token(NUMERO, '20')
              Token(DELIM, ';')            Token(EOF, '')

 ¿CÓMO LO HACE?
   1. Cada tipo de token tiene una EXPRESIÓN REGULAR (su patrón).
   2. Todas se unen en una sola expresión regular "maestra".
   3. Se recorre el texto de izquierda a derecha; en cada posición se
      prueban los patrones EN ORDEN y gana el primero que coincide.
   4. Espacios y comentarios se descartan; un carácter que ningún
      patrón reconoce es un ERROR LÉXICO y detiene el análisis.

 ¿QUÉ ES MÍO?
   - Entrega 1: PR_SI, PR_MIENTRAS, PR_IMPRIMIR y OP_REL.
   - Entrega 2: los 18 tokens de mi catálogo de expansión
     (tokens_catalogo.pdf), marcados abajo con [EXTENSIÓN].
==========================================================================
"""
import re
from typing import List
from .token import Token


def _reservada(palabra: str) -> str:
    """Patrón para una palabra reservada exacta.

    \\b es un "límite de palabra": obliga a que la palabra esté completa.
    Gracias a eso 'nota' se reconoce como ID y NO como la palabra
    reservada 'no' seguida de 'ta'.
    """
    return rf'\b{palabra}\b'


class Lexer:

    def __init__(self, codigo_fuente: str):

        self.codigo = codigo_fuente
        self.tokens: List[Token] = []

        # ------------------------------------------------------------------
        # TABLA DE TOKENS: (NOMBRE, PATRÓN)
        # ¡EL ORDEN IMPORTA! Se prueban de arriba hacia abajo:
        #   * Comentarios antes que OP_ARIT  -> '//' no es dos divisiones '/'
        #   * NUMERO_DECIMAL antes que NUMERO -> '3.14' no se corta en '3'
        #   * Palabras reservadas antes que ID -> 'si' no es un identificador
        #   * OP_REL antes que ASIGNACION      -> '==' no son dos '='
        # ------------------------------------------------------------------
        self.esquema_tokens = [
                # ---------- Comentarios (se descartan) [EXTENSIÓN] ----------
                ('COMENTARIO_BLOQUE', r'/\*[\s\S]*?\*/'),   # /* ... */
                ('COMENTARIO_LINEA',  r'//[^\n]*'),         # // ...

                # ---------- Literales [EXTENSIÓN] ----------
                ('CADENA_LITERAL',    r'"[^"\n]*"'),        # "Hola Mundo"
                ('NUMERO_DECIMAL',    r'\d+\.\d+'),         # 3.14

                # ---------- Palabras reservadas base ----------
                ('PR_ENTERO',         _reservada('entero')),    # del docente
                ('PR_SI',             _reservada('si')),        # Entrega 1
                ('PR_MIENTRAS',       _reservada('mientras')),  # Entrega 1
                ('PR_IMPRIMIR',       _reservada('imprimir')),  # Entrega 1

                # ---------- Palabras reservadas [EXTENSIÓN] ----------
                ('PR_CADENA',         _reservada('cadena')),     # tipo de dato
                ('PR_DECIMAL',        _reservada('decimal')),    # tipo de dato
                ('PR_BOOLEANO',       _reservada('booleano')),   # tipo de dato
                ('PR_SINO',           _reservada('sino')),       # rama falsa del si
                ('PR_ENTONCES',       _reservada('entonces')),   # opcional en el si
                ('PR_PARAR',          _reservada('parar')),      # como break
                ('PR_CONTINUAR',      _reservada('continuar')),  # como continue
                ('PR_FUNCION',        _reservada('funcion')),    # definir función
                ('PR_RETORNAR',       _reservada('retornar')),   # devolver valor
                ('PR_LEER',           _reservada('leer')),       # entrada de datos
                ('BOOLEANO',          r'\b(?:verdadero|falso)\b'),
                ('OP_LOGICO_Y',       _reservada('y')),
                ('OP_LOGICO_O',       _reservada('o')),
                ('OP_LOGICO_NO',      _reservada('no')),

                # ---------- Números e identificadores ----------
                ('NUMERO',            r'\d+'),                     # 20
                ('ID',                r'[a-zA-Z_][a-zA-Z0-9_]*'),  # edad, total_1

                # ---------- Operadores ----------
                ('OP_REL',            r'==|!=|<=|>=|<|>'),  # Entrega 1
                ('OP_ARIT',           r'[+\-*/]'),
                ('ASIGNACION',        r'='),

                # Delimitadores. La coma ',' la agregué en la Entrega 2 para
                # separar parámetros y argumentos de las funciones.
                ('DELIM',             r'[();{},]'),

                # ---------- Se ignoran o son errores ----------
                ('ESPACIO',           r'[ \t]+'),
                ('NUEVA_LINEA',       r'\r\n|\n|\r'),   # solo cuenta líneas
                ('ERROR',             r'.'),            # cualquier otro carácter
        ]

        # Une todos los patrones en UNA expresión regular con grupos con
        # nombre: (?P<PR_SI>\bsi\b)|(?P<ID>...)|...
        # match.lastgroup dice después qué patrón ganó.
        self.regex_maestro = re.compile(
            '|'.join(
                f'(?P<{nombre}>{patron})'
                for nombre, patron in self.esquema_tokens
            )
        )

    def analizar(self) -> List[Token]:
        """Recorre todo el código y devuelve la lista de tokens.

        La lista SIEMPRE termina con un token EOF (fin de archivo), que el
        parser usa para saber que el programa terminó.
        """
        self.tokens = []
        numero_linea = 1

        # finditer recorre el texto y en cada posición aplica la regex maestra
        for match in self.regex_maestro.finditer(self.codigo):

            tipo = match.lastgroup   # nombre del patrón que coincidió
            valor = match.group()    # el texto exacto (lexema)

            if tipo == 'NUEVA_LINEA':
                # No es token: solo sirve para reportar la línea de errores
                numero_linea += 1

            elif tipo == 'ESPACIO':
                continue

            elif tipo in ('COMENTARIO_LINEA', 'COMENTARIO_BLOQUE'):
                # Los comentarios NO generan token (por eso el parser no
                # necesita reglas para ellos). Un comentario /* */ puede
                # ocupar varias líneas, así que se cuentan sus saltos.
                numero_linea += valor.count('\n')

            elif tipo == 'ERROR':
                # Ningún patrón reconoció el carácter: error léxico
                raise RuntimeError(
                    f"[Error Lexico] "
                    f"Caracter inesperado '{valor}' "
                    f"en linea {numero_linea}"
                )

            else:
                # Cualquier otro patrón produce un token
                self.tokens.append(Token(tipo, valor, numero_linea))

        self.tokens.append(Token('EOF', '', numero_linea))
        return self.tokens
