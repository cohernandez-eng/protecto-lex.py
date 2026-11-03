
"""
==========================================================================
 MAIN.PY: PUNTO DE ENTRADA DEL COMPILADOR
==========================================================================
 Autor: Celso Otoniel Hernández - Carné 2400455

 Une las tres fases en orden:

   código fuente (.txt)
        |
        v
   FASE 1: Lexer  (lexer/lexer.py)    -> lista de tokens
        |
        v
   FASE 2: Parser (parser/parser.py)  -> AST (arbol_ast/nodos.py)
        |
        v
   FASE 3: Semántica (semantic/analizador.py) -> tabla de símbolos

 Uso:  python main.py pruebas/07_extension_personal.txt
       python main.py --solo-lexer  archivo.txt   (solo Fase 1)
       python main.py --solo-parser archivo.txt   (Fases 1 y 2)
 No ejecuta el programa: sin TAC ni máquina virtual.
==========================================================================
"""
import argparse
from pathlib import Path
from lexer.lexer import Lexer          # FASE 1: mi analizador léxico
from parser.parser import Parser       # FASE 2: mi analizador sintáctico
from semantic.analizador import AnalizadorSemantico  # FASE 3: mi analizador semántico
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


def imprimir_tabla_simbolos(semantico):
    """Muestra la tabla de símbolos como tabla de texto."""
    filas = [(nombre, 'variable', tipo) for nombre, tipo in semantico.tabla_simbolos.items()]
    for nombre, (retorno, params) in semantico.tabla_funciones.items():
        firma = f"{retorno} ({', '.join(params) or 'sin parametros'})"
        filas.append((nombre, 'funcion', firma))
    if not filas:
        print('  (vacia)')
        return
    ancho = [max(len(f[i]) for f in filas + [('Nombre', 'Categoria', 'Tipo')]) for i in range(3)]
    linea = '  +' + '+'.join('-' * (a + 2) for a in ancho) + '+'
    fmt = '  | ' + ' | '.join('{:<' + str(a) + '}' for a in ancho) + ' |'
    print(linea)
    print(fmt.format('Nombre', 'Categoria', 'Tipo'))
    print(linea)
    for f in filas:
        print(fmt.format(*f))
    print(linea)


def analizar_semantica(arbol):
    print('\n=== FASE 3 - ANALISIS SEMANTICO (semantic/analizador.py) ===')
    semantico = AnalizadorSemantico()
    semantico.analizar(arbol)
    print('Analisis semantico correcto.')
    print('Tabla de simbolos:', semantico.tabla_simbolos)
    if semantico.tabla_funciones:
        print('Tabla de funciones:', semantico.tabla_funciones)
    print()
    imprimir_tabla_simbolos(semantico)
    return semantico


def main():
    argumentos = argparse.ArgumentParser(description='Lexer + Parser + Semantica')
    argumentos.add_argument('archivo', nargs='?', default='pruebas/01_basico_valido.txt')
    argumentos.add_argument('--solo-lexer', action='store_true',
                            help='Ejecutar unicamente el analizador lexico.')
    argumentos.add_argument('--solo-parser', action='store_true',
                            help='Ejecutar lexer + parser, sin semantica.')
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
    print('=== MI COMPILADOR: LEXER + PARSER + SEMANTICA ===')
    print('\nCODIGO FUENTE:')
    print(codigo)
    try:
        tokens = analizar_lexico(codigo)
        if opciones.solo_lexer:
            print('\nEjecucion detenida despues del lexer.')
            return 0
        arbol = analizar_sintactico(tokens)
        if opciones.solo_parser:
            print('\nEjecucion detenida despues del parser.')
            return 0
        analizar_semantica(arbol)
        print('\nLas tres fases finalizaron correctamente.')
        return 0
    except NotImplementedError as error:
        print(f'\n[IMPLEMENTACION PENDIENTE] {error}')
        return 2
    except (RuntimeError, SyntaxError, ValueError, NameError, TypeError) as error:
        print(f'\n{error}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
