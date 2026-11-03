"""Pruebas de la NUEVA fase semántica. No editar para ocultar fallos.

Correr: python -m unittest pruebas.test_semantica -v
"""
import unittest
from lexer.lexer import Lexer
from parser.parser import Parser
from semantic.analizador import AnalizadorSemantico
from arbol_ast.nodos import Numero

def analizar(codigo):
    arbol = Parser(Lexer(codigo).analizar()).parsear()
    sem = AnalizadorSemantico()
    sem.analizar(arbol)
    return sem

class TestEstructuraEntregada(unittest.TestCase):
    def test_tabla_inicial_vacia(self):
        self.assertEqual(AnalizadorSemantico().tabla_simbolos, {})

    def test_numero_entero(self):
        self.assertEqual(AnalizadorSemantico().analizar(Numero(12)), 'entero')

class TestDeclaraciones(unittest.TestCase):
    def test_declaracion_valida(self):
        self.assertEqual(analizar('entero edad = 20;').tabla_simbolos, {'edad': 'entero'})

    def test_duplicada(self):
        with self.assertRaises(NameError):
            analizar('entero x = 1; entero x = 2;')

    def test_autorreferencia_no_declarada(self):
        with self.assertRaises(NameError):
            analizar('entero x = x + 1;')

class TestAsignaciones(unittest.TestCase):
    def test_asignacion_valida(self):
        self.assertEqual(analizar('entero x = 5; x = x + 1;').tabla_simbolos, {'x': 'entero'})

    def test_asignacion_no_declarada(self):
        with self.assertRaises(NameError):
            analizar('x = 10;')

    def test_variable_inexistente_en_expresion(self):
        with self.assertRaises(NameError):
            analizar('entero x = y + 5;')

class TestTipos(unittest.TestCase):
    def test_operacion_aritmetica_es_entero(self):
        analizar('entero resultado = 5 + 3 * 2;')

    def test_comparacion_como_condicion(self):
        analizar('entero x = 5; si (x < 10) { imprimir(x); }')

    def test_inicializacion_incompatible(self):
        with self.assertRaises(TypeError):
            analizar('entero x = 5 < 10;')

    def test_asignacion_incompatible(self):
        with self.assertRaises(TypeError):
            analizar('entero x = 5; x = x < 10;')

    def test_operacion_bool_entero_invalida(self):
        with self.assertRaises(TypeError):
            analizar('entero x = (1 < 2) + 3;')

    def test_condicion_entero_invalida(self):
        with self.assertRaises(TypeError):
            analizar('entero x = 3; si (x) { imprimir(x); }')

    def test_comparacion_encadenada_no_soportada(self):
        with self.assertRaises(TypeError):
            analizar('entero x = 3; si (1 < x < 5) { imprimir(x); }')

class TestControl(unittest.TestCase):
    def test_mientras_valido(self):
        sem = analizar('entero x = 0; mientras (x < 3) { x = x + 1; }')
        self.assertEqual(sem.tabla_simbolos, {'x': 'entero'})

    def test_mientras_condicion_no_booleana(self):
        with self.assertRaises(TypeError):
            analizar('entero x = 0; mientras (x) { x = 1; }')

    def test_imprimir_identificador_inexistente(self):
        with self.assertRaises(NameError):
            analizar('imprimir(fantasma);')

if __name__ == '__main__':
    unittest.main()
