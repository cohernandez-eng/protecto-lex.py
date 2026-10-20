"""Pruebas de la extensión personal (tokens adicionales del lexer).

No modifica test_integracion.py del docente. Ejecutar con:
    python -m unittest pruebas.test_extension -v
"""
import unittest

from lexer.lexer import Lexer
from parser.parser import Parser
from arbol_ast.nodos import (
    Declaracion, Numero, Identificador, OpBinaria, Imprimir, Si, Mientras,
    Decimal, Cadena, Booleano, OpUnaria, Leer, Parar, Continuar,
    Parametro, Funcion, Retornar, LlamadaFuncion,
)


def analizar(codigo):
    return Parser(Lexer(codigo).analizar()).parsear()


def tipos(codigo):
    return [t.tipo for t in Lexer(codigo).analizar()]


class TestLexerExtension(unittest.TestCase):
    def test_tokens_del_catalogo(self):
        self.assertEqual(
            tipos('decimal cadena booleano sino entonces parar continuar '
                  'funcion retornar leer verdadero falso y o no'),
            ['PR_DECIMAL', 'PR_CADENA', 'PR_BOOLEANO', 'PR_SINO', 'PR_ENTONCES',
             'PR_PARAR', 'PR_CONTINUAR', 'PR_FUNCION', 'PR_RETORNAR', 'PR_LEER',
             'BOOLEANO', 'BOOLEANO', 'OP_LOGICO_Y', 'OP_LOGICO_O',
             'OP_LOGICO_NO', 'EOF'])

    def test_literales(self):
        self.assertEqual(tipos('3.14 "Hola Mundo" 42'),
                         ['NUMERO_DECIMAL', 'CADENA_LITERAL', 'NUMERO', 'EOF'])

    def test_comentarios_se_descartan_y_cuentan_lineas(self):
        tokens = Lexer('// linea\n/* bloque\n de dos */ entero x = 1;').analizar()
        self.assertEqual(tokens[0].tipo, 'PR_ENTERO')
        self.assertEqual(tokens[0].linea, 3)

    def test_palabra_reservada_no_es_prefijo(self):
        # 'sinodal' y 'nota' deben ser ID, no 'sino' + ... ni 'no' + ...
        self.assertEqual(tipos('sinodal nota'), ['ID', 'ID', 'EOF'])


class TestParserExtension(unittest.TestCase):
    def test_declaraciones_de_nuevos_tipos(self):
        ast = analizar('decimal pi = 3.14; cadena s = "hola"; booleano b = falso;')
        self.assertEqual(ast.sentencias[0].expr, Decimal(3.14))
        self.assertEqual(ast.sentencias[1].expr, Cadena('hola'))
        self.assertEqual(ast.sentencias[2].expr, Booleano(False))
        self.assertEqual([d.tipo for d in ast.sentencias],
                         ['decimal', 'cadena', 'booleano'])

    def test_si_sino(self):
        nodo = analizar('si (x > 1) { imprimir(1); } sino { imprimir(0); }').sentencias[0]
        self.assertIsInstance(nodo, Si)
        self.assertEqual(nodo.bloque_f, [Imprimir(Numero(0))])

    def test_sino_si_encadenado(self):
        nodo = analizar('si (x > 1) { } sino si (x > 0) { } sino { }').sentencias[0]
        self.assertIsInstance(nodo.bloque_f[0], Si)
        self.assertEqual(nodo.bloque_f[0].bloque_f, [])

    def test_entonces_opcional(self):
        con = analizar('si (x == 1) entonces { imprimir(x); }').sentencias[0]
        sin = analizar('si (x == 1) { imprimir(x); }').sentencias[0]
        self.assertEqual(con, sin)

    def test_precedencia_logica(self):
        # a o b y no c  ==  a o (b y (no c))
        expr = analizar('booleano r = a o b y no c;').sentencias[0].expr
        self.assertEqual(expr, OpBinaria(
            Identificador('a', 1), 'o',
            OpBinaria(Identificador('b', 1), 'y',
                      OpUnaria('no', Identificador('c', 1)))))

    def test_logico_menor_precedencia_que_relacional(self):
        expr = analizar('booleano r = x < 1 y x > 5;').sentencias[0].expr
        self.assertEqual(expr.op, 'y')
        self.assertEqual((expr.izq.op, expr.der.op), ('<', '>'))

    def test_menos_unario(self):
        expr = analizar('entero x = -2 * 3;').sentencias[0].expr
        self.assertEqual(expr, OpBinaria(OpUnaria('-', Numero(2)), '*', Numero(3)))

    def test_leer_parar_continuar(self):
        ast = analizar('leer x; mientras (verdadero) { continuar; parar; }')
        self.assertEqual(ast.sentencias[0], Leer('x', 1))
        bloque = ast.sentencias[1].bloque
        self.assertIsInstance(ast.sentencias[1], Mientras)
        self.assertEqual(bloque, [Continuar(1), Parar(1)])

    def test_funcion_y_llamada(self):
        ast = analizar('funcion entero suma(entero a, entero b) { retornar a + b; }'
                       'entero r = suma(1, 2); suma(3, 4);')
        f = ast.sentencias[0]
        self.assertIsInstance(f, Funcion)
        self.assertEqual(f.parametros, [Parametro('entero', 'a'), Parametro('entero', 'b')])
        self.assertIsInstance(f.cuerpo[0], Retornar)
        self.assertEqual(ast.sentencias[1].expr,
                         LlamadaFuncion('suma', [Numero(1), Numero(2)], 1))
        self.assertIsInstance(ast.sentencias[2], LlamadaFuncion)

    def test_retornar_sin_valor(self):
        f = analizar('funcion entero f() { retornar; }').sentencias[0]
        self.assertEqual(f.cuerpo, [Retornar(None, 1)])


class TestErroresExtension(unittest.TestCase):
    def test_sino_sin_si(self):
        with self.assertRaises(SyntaxError):
            analizar('sino { imprimir(1); }')

    def test_funcion_sin_coma(self):
        with self.assertRaises(SyntaxError):
            analizar('funcion entero f(entero a entero b) { }')

    def test_logico_sin_operando(self):
        with self.assertRaises(SyntaxError):
            analizar('booleano r = x y ;')

    def test_parar_sin_punto_y_coma(self):
        with self.assertRaises(SyntaxError):
            analizar('mientras (verdadero) { parar }')

    def test_leer_sin_identificador(self):
        with self.assertRaises(SyntaxError):
            analizar('leer 5;')

    def test_cadena_sin_cerrar_es_error_lexico(self):
        with self.assertRaises(RuntimeError):
            Lexer('cadena s = "hola;').analizar()


if __name__ == '__main__':
    unittest.main()
