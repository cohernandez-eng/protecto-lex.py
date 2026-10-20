
"""
==========================================================================
 MAIN.PY: PUNTO DE ENTRADA DEL COMPILADOR
==========================================================================
 Autor: Celso Otoniel Hernández - Carné 2400455

 Une las dos fases en orden:

   código fuente (.txt)
        |
        v
   FASE 1: Lexer  (lexer/lexer.py)    -> lista de tokens
        |
        v
   FASE 2: Parser (parser/parser.py)  -> AST (arbol_ast/nodos.py)

 Uso:  python main.py pruebas/07_extension_personal.txt
 No ejecuta el programa ni hace análisis semántico (próxima entrega).
==========================================================================
"""
import argparse
from pathlib import Path
from lexer.lexer import Lexer          # FASE 1: mi analizador léxico
from parser.parser import Parser       # FASE 2: mi analizador sintáctico
from arbol_ast.imprimir_arbol import arbol_texto  # dibuja el AST en consola

BASE_DIR = Path(__file__).resolve().parent
MOSTRAR_REPR = False


def analizar_lexico(codigo):
    print('\n=== FASE 1 - ANALISIS LEXICO (lexer/lexer.py) ===')
    tokens = Lexer(codigo).analizar()
    for token in tokens:
        print(' ', token)
    return tokens


def analizar_sintactico(tokens):
    print('\n=== FASE 2 - ANALISIS SINTACTICO (parser/parser.py) ===')
    arbol = Parser(tokens).parsear()
    print('Analisis sintactico correcto. AST generado:\n')
    print(arbol_texto(arbol))
    if MOSTRAR_REPR:
        print('\nAST (representacion de Python):')
        print(arbol)
    return arbol


def main():
    argumentos = argparse.ArgumentParser(description='Lexer + Parser + AST')
    argumentos.add_argument('archivo', nargs='?', default='pruebas/01_basico_valido.txt')
    argumentos.add_argument('--solo-lexer', action='store_true')
    argumentos.add_argument('--repr', action='store_true',
                            help='Ademas del arbol, imprime el AST con repr()')
    opciones = argumentos.parse_args()
    global MOSTRAR_REPR
    MOSTRAR_REPR = opciones.repr
    ruta = Path(opciones.archivo)
    if not ruta.is_absolute() and not ruta.exists():
        ruta = BASE_DIR / ruta
    try:
        codigo = ruta.read_text(encoding='utf-8')
    except OSError as error:
        print(f'No se pudo abrir el archivo: {error}')
        return 1
    print('=== MI COMPILADOR: LEXER + PARSER ===')
    print('\nCODIGO FUENTE:')
    print(codigo)
    try:
        tokens = analizar_lexico(codigo)
        if opciones.solo_lexer:
            print('\nDetenido después del lexer.')
            return 0
        analizar_sintactico(tokens)
        print('\nLa fase semántica está pendiente para la siguiente entrega.')
        return 0
    except NotImplementedError as error:
        print(f'\n[IMPLEMENTACION PENDIENTE] {error}')
        return 2
    except (RuntimeError, SyntaxError, ValueError) as error:
        print(f'\n{error}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
