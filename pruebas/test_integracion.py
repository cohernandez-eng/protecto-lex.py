"""Pruebas graduales: algunas fallarán hasta que completes los TODO."""
import unittest

from lexer.lexer import Lexer
from parser.parser import Parser
from arbol_ast.nodos import (
    Programa, Declaracion, Asignacion, Numero, OpBinaria,
    Imprimir, Si, Mientras,
)


def analizar(codigo):
    return Parser(Lexer(codigo).analizar()).parsear()


class TestLexer(unittest.TestCase):
    def test_tokens_basicos(self):
        tipos = [t.tipo for t in Lexer('entero x = 10;').analizar()]
        self.assertEqual(tipos, ['PR_ENTERO', 'ID', 'ASIGNACION', 'NUMERO', 'DELIM', 'EOF'])

    def test_error_lexico(self):
        with self.assertRaises(RuntimeError):
            Lexer('entero x = 1 @ 2;').analizar()


class TestParserBasico(unittest.TestCase):
    def test_declaracion(self):
        ast = analizar('entero edad = 20;')
        self.assertIsInstance(ast, Programa)
        self.assertEqual(len(ast.sentencias), 1)
        nodo = ast.sentencias[0]
        self.assertIsInstance(nodo, Declaracion)
        self.assertEqual((nodo.tipo, nodo.id, nodo.linea), ('entero', 'edad', 1))
        self.assertEqual(nodo.expr, Numero(20))

    def test_asignacion(self):
        ast = analizar('entero x = 1; x = 5;')
        self.assertIsInstance(ast.sentencias[1], Asignacion)
        self.assertEqual(ast.sentencias[1].expr, Numero(5))

    def test_sintaxis_no_es_semantica(self):
        ast = analizar('x = 10;')
        self.assertIsInstance(ast.sentencias[0], Asignacion)


class TestExpresiones(unittest.TestCase):
    def test_precedencia(self):
        expr = analizar('entero resultado = 5 + 3 * 2;').sentencias[0].expr
        self.assertEqual(expr, OpBinaria(Numero(5), '+', OpBinaria(Numero(3), '*', Numero(2))))

    def test_parentesis(self):
        expr = analizar('entero x = (5 + 3) * 2;').sentencias[0].expr
        self.assertEqual(expr, OpBinaria(OpBinaria(Numero(5), '+', Numero(3)), '*', Numero(2)))

    def test_asociatividad(self):
        expr = analizar('entero x = 1 - 2 - 3;').sentencias[0].expr
        self.assertEqual(expr, OpBinaria(OpBinaria(Numero(1), '-', Numero(2)), '-', Numero(3)))


class TestControl(unittest.TestCase):
    def test_imprimir(self):
        self.assertEqual(analizar('imprimir(10);').sentencias[0], Imprimir(Numero(10)))

    def test_mientras(self):
        ast = analizar('mientras (x < 3) { x = x + 1; }')
        self.assertIsInstance(ast.sentencias[0], Mientras)
        self.assertEqual(len(ast.sentencias[0].bloque), 1)

    def test_si(self):
        ast = analizar('si (x == 3) { imprimir(x); }')
        self.assertIsInstance(ast.sentencias[0], Si)
        self.assertIsInstance(ast.sentencias[0].bloque_v[0], Imprimir)


class TestErrores(unittest.TestCase):
    def test_falta_punto_y_coma(self):
        with self.assertRaises(SyntaxError):
            analizar('entero x = 10')

    def test_falta_identificador(self):
        with self.assertRaises(SyntaxError):
            analizar('entero = 10;')

    def test_bloque_sin_cerrar(self):
        with self.assertRaises(SyntaxError):
            analizar('mientras (x < 3) { x = 2;')


if __name__ == '__main__':
    unittest.main()
