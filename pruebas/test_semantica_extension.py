"""Pruebas semánticas de MI EXTENSIÓN PERSONAL (Entrega 3).

No modifica test_semantica.py del docente. Ejecutar con:
    python -m unittest pruebas.test_semantica_extension -v
"""
import unittest

from lexer.lexer import Lexer
from parser.parser import Parser
from semantic.analizador import AnalizadorSemantico


def analizar(codigo):
    arbol = Parser(Lexer(codigo).analizar()).parsear()
    sem = AnalizadorSemantico()
    sem.analizar(arbol)
    return sem


class TestEquivalenteDocente(unittest.TestCase):
    def test_variable_inexistente_con_otro_nombre(self):
        # Misma idea que test_variable_inexistente_en_expresion del docente,
        # con 'z' porque en mi lenguaje 'y' es palabra reservada.
        with self.assertRaises(NameError):
            analizar('entero x = z + 5;')

    def test_y_es_reservada_en_mi_lenguaje(self):
        # Documenta por qué la prueba del docente con 'y' no llega a la semántica.
        with self.assertRaises(SyntaxError):
            analizar('entero x = y + 5;')


class TestTiposNuevos(unittest.TestCase):
    def test_tabla_con_todos_los_tipos(self):
        sem = analizar('decimal d = 3.14; cadena c = "hola"; booleano b = falso; entero e = 1;')
        self.assertEqual(sem.tabla_simbolos,
                         {'d': 'decimal', 'c': 'cadena', 'b': 'booleano', 'e': 'entero'})

    def test_entero_cabe_en_decimal(self):
        self.assertEqual(analizar('decimal d = 5;').tabla_simbolos, {'d': 'decimal'})

    def test_decimal_no_cabe_en_entero(self):
        with self.assertRaises(TypeError):
            analizar('entero e = 2.5;')

    def test_entero_mas_decimal_es_decimal(self):
        analizar('decimal d = 1 + 2.5;')
        with self.assertRaises(TypeError):
            analizar('entero e = 1 + 2.5;')

    def test_concatenar_cadenas(self):
        analizar('cadena s = "Hola " + "Ana";')
        with self.assertRaises(TypeError):
            analizar('cadena s = "Hola" - "a";')

    def test_cadena_mas_numero_invalido(self):
        with self.assertRaises(TypeError):
            analizar('cadena s = "edad: " + 20;')

    def test_booleano_como_condicion(self):
        analizar('si (verdadero) { imprimir(1); }')

    def test_igualdad_de_cadenas(self):
        analizar('cadena a = "x"; si (a == "x") { imprimir(a); }')
        with self.assertRaises(TypeError):
            analizar('cadena a = "x"; si (a == 5) { imprimir(a); }')


class TestLogicos(unittest.TestCase):
    def test_y_o_no_validos(self):
        analizar('entero x = 5; si (x > 1 y no (x == 3) o falso) { imprimir(x); }')

    def test_y_con_entero_invalido(self):
        with self.assertRaises(TypeError):
            analizar('entero x = 5; si (x y verdadero) { imprimir(x); }')

    def test_no_con_numero_invalido(self):
        with self.assertRaises(TypeError):
            analizar('booleano b = no 5;')

    def test_menos_unario(self):
        analizar('decimal d = -2.5;')
        with self.assertRaises(TypeError):
            analizar('booleano b = -verdadero;')


class TestSinoYCiclos(unittest.TestCase):
    def test_sino_se_revisa(self):
        # El error está en la rama 'sino': también debe detectarse.
        with self.assertRaises(NameError):
            analizar('si (verdadero) { imprimir(1); } sino { imprimir(fantasma); }')

    def test_sino_si_condicion_no_booleana(self):
        with self.assertRaises(TypeError):
            analizar('entero x = 1; si (x > 0) { } sino si (x) { }')

    def test_parar_y_continuar_dentro_de_ciclo(self):
        analizar('mientras (verdadero) { continuar; parar; }')

    def test_parar_fuera_de_ciclo(self):
        with self.assertRaises(ValueError):
            analizar('parar;')

    def test_continuar_en_si_fuera_de_ciclo(self):
        with self.assertRaises(ValueError):
            analizar('si (verdadero) { continuar; }')

    def test_leer_variable_declarada(self):
        analizar('entero x = 0; leer x;')
        with self.assertRaises(NameError):
            analizar('leer x;')


class TestFunciones(unittest.TestCase):
    def test_funcion_valida_y_tabla(self):
        sem = analizar('funcion entero suma(entero a, entero b) { retornar a + b; }'
                       'entero r = suma(1, 2);')
        self.assertEqual(sem.tabla_funciones, {'suma': ('entero', ['entero', 'entero'])})
        # Los parámetros no quedan en la tabla global
        self.assertEqual(sem.tabla_simbolos, {'r': 'entero'})

    def test_recursion_permitida(self):
        analizar('funcion entero f(entero n) { retornar f(n - 1); }')

    def test_funcion_no_declarada(self):
        with self.assertRaises(NameError):
            analizar('entero r = suma(1, 2);')

    def test_cantidad_de_argumentos(self):
        with self.assertRaises(TypeError):
            analizar('funcion entero f(entero n) { retornar n; } entero r = f(1, 2);')

    def test_tipo_de_argumento(self):
        with self.assertRaises(TypeError):
            analizar('funcion entero f(entero n) { retornar n; } entero r = f("uno");')

    def test_tipo_de_retorno(self):
        with self.assertRaises(TypeError):
            analizar('funcion entero f() { retornar "hola"; }')

    def test_retornar_sin_valor(self):
        with self.assertRaises(TypeError):
            analizar('funcion entero f() { retornar; }')

    def test_retornar_fuera_de_funcion(self):
        with self.assertRaises(ValueError):
            analizar('retornar 1;')

    def test_funcion_duplicada(self):
        with self.assertRaises(NameError):
            analizar('funcion entero f() { retornar 1; } funcion entero f() { retornar 2; }')

    def test_parametro_repetido(self):
        with self.assertRaises(NameError):
            analizar('funcion entero f(entero a, entero a) { retornar a; }')

    def test_resultado_de_funcion_con_tipo(self):
        with self.assertRaises(TypeError):
            analizar('funcion booleano es() { retornar verdadero; } entero x = es();')


class TestComentariosNoAfectan(unittest.TestCase):
    def test_comentarios_no_llegan_a_la_semantica(self):
        sem = analizar('// comentario\nentero x = 1; /* otro */')
        self.assertEqual(sem.tabla_simbolos, {'x': 'entero'})


if __name__ == '__main__':
    unittest.main()
