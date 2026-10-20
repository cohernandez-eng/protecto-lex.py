"""Analizador sintáctico descendente recursivo (Entrega 2: Lexer + Parser + AST).

Autor: Celso Otoniel Hernández - Carné 2400455

Etapa A: declaraciones y asignaciones.            (TODO 1 - 4)
Etapa B: expresiones y precedencia.               (TODO 5 - 8)
Etapa C: imprimir, si, mientras y bloques.        (TODO 9 - 12)
Etapa D: extensión personal con los tokens adicionales del lexer
         (tipos decimal/cadena/booleano, literales, sino, entonces,
          operadores lógicos y/o/no, leer, parar, continuar,
          funcion/retornar y llamadas a función).

Gramática completa: ver README.md, sección "Gramática implementada".
"""
from typing import List, Optional
from lexer.token import Token
from arbol_ast.nodos import (
    NodoAST, Programa, Declaracion, Asignacion, Numero, Identificador,
    OpBinaria, Imprimir, Si, Mientras,
    # Extensión personal
    Decimal, Cadena, Booleano, OpUnaria, Leer, Parar, Continuar,
    Parametro, Funcion, Retornar, LlamadaFuncion,
)


# Tokens que inician una declaración: 'entero' (base) + tipos de expansión.
TIPOS_DATO = ('PR_ENTERO', 'PR_DECIMAL', 'PR_CADENA', 'PR_BOOLEANO')


class Parser:
    def __init__(self, tokens: List[Token]):
        if not tokens or tokens[-1].tipo != 'EOF':
            raise ValueError('El parser necesita una lista de tokens terminada en EOF.')
        self.tokens = tokens
        self.pos = 0
        self.token_actual = tokens[0]

    # ------------------------------------------------------------------
    # Proporcionados por el docente
    # ------------------------------------------------------------------
    def avanzar(self):
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
            self.token_actual = self.tokens[self.pos]

    def coincidir(self, valor_esperado: str) -> Token:
        actual = self.token_actual
        if actual.tipo == valor_esperado or actual.valor == valor_esperado:
            self.avanzar()
            return actual
        encontrado = actual.valor if actual.tipo != 'EOF' else 'EOF'
        raise SyntaxError(
            f"[Error Sintactico] Linea {actual.linea}: "
            f"se esperaba '{valor_esperado}', se encontro '{encontrado}' "
            f"(tipo: {actual.tipo})."
        )

    # ------------------------------------------------------------------
    # Auxiliares propios
    # ------------------------------------------------------------------
    def es(self, *esperados: str) -> bool:
        """True si el token actual coincide (por tipo o valor) con alguno."""
        return any(self.token_actual.tipo == e or self.token_actual.valor == e
                   for e in esperados)

    def siguiente(self) -> Token:
        """Mira el token siguiente sin consumirlo (lookahead de 1)."""
        return self.tokens[min(self.pos + 1, len(self.tokens) - 1)]

    def error(self, mensaje: str):
        actual = self.token_actual
        encontrado = actual.valor if actual.tipo != 'EOF' else 'EOF'
        raise SyntaxError(
            f"[Error Sintactico] Linea {actual.linea}: {mensaje}, "
            f"se encontro '{encontrado}' (tipo: {actual.tipo})."
        )

    # ==================================================================
    # ETAPA A - PARSER BÁSICO
    # ==================================================================
    def parsear(self) -> Programa:
        """TODO 1: programa → sentencia* EOF"""
        sentencias = []
        while self.token_actual.tipo != 'EOF':
            sentencias.append(self.sentencia())
        self.coincidir('EOF')
        return Programa(sentencias)

    def sentencia(self) -> NodoAST:
        """TODO 2: elegir la regla según el token actual."""
        tipo = self.token_actual.tipo

        if tipo in TIPOS_DATO:
            return self.declaracion()
        if tipo == 'ID':
            # Lookahead: ID '(' → llamada a función; ID '=' → asignación.
            if self.siguiente().valor == '(':
                return self.sentencia_llamada()
            return self.asignacion()
        if tipo == 'PR_IMPRIMIR':
            return self.sentencia_imprimir()
        if tipo == 'PR_SI':
            return self.sentencia_si()
        if tipo == 'PR_MIENTRAS':
            return self.sentencia_mientras()

        # ---- Extensión personal ----
        if tipo == 'PR_LEER':
            return self.sentencia_leer()
        if tipo == 'PR_PARAR':
            return self.sentencia_parar()
        if tipo == 'PR_CONTINUAR':
            return self.sentencia_continuar()
        if tipo == 'PR_FUNCION':
            return self.sentencia_funcion()
        if tipo == 'PR_RETORNAR':
            return self.sentencia_retornar()
        if tipo == 'PR_SINO':
            self.error("'sino' sin un 'si' previo")

        self.error('se esperaba el inicio de una sentencia')

    def declaracion(self) -> Declaracion:
        """TODO 3: tipo ID '=' expresion ';'   (tipo: entero|decimal|cadena|booleano)"""
        if not self.es(*TIPOS_DATO):
            self.error('se esperaba un tipo de dato')
        tok_tipo = self.token_actual
        self.avanzar()
        tok_id = self.coincidir('ID')
        self.coincidir('=')
        expr = self.expresion()
        self.coincidir(';')
        return Declaracion(tok_tipo.valor, tok_id.valor, expr, tok_tipo.linea)

    def asignacion(self) -> Asignacion:
        """TODO 4: ID '=' expresion ';'"""
        tok_id = self.coincidir('ID')
        self.coincidir('=')
        expr = self.expresion()
        self.coincidir(';')
        return Asignacion(tok_id.valor, expr, tok_id.linea)

    # ==================================================================
    # ETAPA B - EXPRESIONES Y PRECEDENCIA (de menor a mayor)
    #   o  <  y  <  no  <  OP_REL  <  + -  <  * /  <  unario -  <  factor
    # ==================================================================
    def expresion(self) -> NodoAST:
        """TODO 5: punto de entrada de las expresiones.

        Base: aritmetica (OP_REL aritmetica)*. Con la extensión, encima de
        la comparación quedan los niveles lógicos o / y / no.
        """
        return self.logica_o()

    def logica_o(self) -> NodoAST:
        """EXT: logica_o → logica_y ('o' logica_y)*"""
        nodo = self.logica_y()
        while self.es('OP_LOGICO_O'):
            op = self.coincidir('OP_LOGICO_O').valor
            nodo = OpBinaria(nodo, op, self.logica_y())
        return nodo

    def logica_y(self) -> NodoAST:
        """EXT: logica_y → negacion ('y' negacion)*"""
        nodo = self.negacion()
        while self.es('OP_LOGICO_Y'):
            op = self.coincidir('OP_LOGICO_Y').valor
            nodo = OpBinaria(nodo, op, self.negacion())
        return nodo

    def negacion(self) -> NodoAST:
        """EXT: negacion → 'no' negacion | comparacion"""
        if self.es('OP_LOGICO_NO'):
            op = self.coincidir('OP_LOGICO_NO').valor
            return OpUnaria(op, self.negacion())
        return self.comparacion()

    def comparacion(self) -> NodoAST:
        """comparacion → aritmetica (OP_REL aritmetica)*   (regla base del TODO 5)"""
        nodo = self.aritmetica()
        while self.es('OP_REL'):
            op = self.coincidir('OP_REL').valor
            nodo = OpBinaria(nodo, op, self.aritmetica())
        return nodo

    def aritmetica(self) -> NodoAST:
        """TODO 6: aritmetica → termino (('+' | '-') termino)*  (asociativa a la izquierda)"""
        nodo = self.termino()
        while self.es('+', '-'):
            op = self.coincidir('OP_ARIT').valor
            nodo = OpBinaria(nodo, op, self.termino())
        return nodo

    def termino(self) -> NodoAST:
        """TODO 7: termino → unario (('*' | '/') unario)*"""
        nodo = self.unario()
        while self.es('*', '/'):
            op = self.coincidir('OP_ARIT').valor
            nodo = OpBinaria(nodo, op, self.unario())
        return nodo

    def unario(self) -> NodoAST:
        """EXT: unario → '-' unario | factor   (permite -5 o -(a + b))"""
        if self.es('-'):
            self.coincidir('-')
            return OpUnaria('-', self.unario())
        return self.factor()

    def factor(self) -> NodoAST:
        """TODO 8: NUMERO | ID | '(' expresion ')'
        EXT: | NUMERO_DECIMAL | CADENA_LITERAL | BOOLEANO | ID '(' argumentos ')'
        """
        tok = self.token_actual

        if tok.tipo == 'NUMERO':
            self.avanzar()
            return Numero(int(tok.valor))
        if tok.tipo == 'ID':
            if self.siguiente().valor == '(':
                return self.llamada_funcion()
            self.avanzar()
            return Identificador(tok.valor, tok.linea)
        if tok.valor == '(':
            self.coincidir('(')
            nodo = self.expresion()
            self.coincidir(')')
            return nodo

        # ---- Extensión personal: literales ----
        if tok.tipo == 'NUMERO_DECIMAL':
            self.avanzar()
            return Decimal(float(tok.valor))
        if tok.tipo == 'CADENA_LITERAL':
            self.avanzar()
            return Cadena(tok.valor[1:-1])
        if tok.tipo == 'BOOLEANO':
            self.avanzar()
            return Booleano(tok.valor == 'verdadero')

        self.error('se esperaba un numero, identificador, literal o (')

    # ==================================================================
    # ETAPA C - CONTROL DE FLUJO
    # ==================================================================
    def sentencia_imprimir(self) -> Imprimir:
        """TODO 9: 'imprimir' '(' expresion ')' ';'"""
        self.coincidir('PR_IMPRIMIR')
        self.coincidir('(')
        expr = self.expresion()
        self.coincidir(')')
        self.coincidir(';')
        return Imprimir(expr)

    def sentencia_si(self) -> Si:
        """TODO 10: 'si' '(' expresion ')' ['entonces'] bloque ['sino' (si | bloque)]"""
        self.coincidir('PR_SI')
        self.coincidir('(')
        condicion = self.expresion()
        self.coincidir(')')
        if self.es('PR_ENTONCES'):          # EXT: 'entonces' opcional
            self.coincidir('PR_ENTONCES')
        bloque_v = self.bloque()

        bloque_f = None
        if self.es('PR_SINO'):              # EXT: rama 'sino'
            self.coincidir('PR_SINO')
            if self.es('PR_SI'):            # 'sino si' encadenado
                bloque_f = [self.sentencia_si()]
            else:
                bloque_f = self.bloque()
        return Si(condicion, bloque_v, bloque_f)

    def sentencia_mientras(self) -> Mientras:
        """TODO 11: 'mientras' '(' expresion ')' bloque"""
        self.coincidir('PR_MIENTRAS')
        self.coincidir('(')
        condicion = self.expresion()
        self.coincidir(')')
        return Mientras(condicion, self.bloque())

    def bloque(self) -> List[NodoAST]:
        """TODO 12: '{' sentencia* '}' — detecta EOF sin cerrar la llave."""
        llave = self.coincidir('{')
        sentencias = []
        while not self.es('}'):
            if self.token_actual.tipo == 'EOF':
                raise SyntaxError(
                    f"[Error Sintactico] Linea {self.token_actual.linea}: "
                    f"se esperaba '}}' para cerrar el bloque abierto en la "
                    f"linea {llave.linea}, se encontro 'EOF'."
                )
            sentencias.append(self.sentencia())
        self.coincidir('}')
        return sentencias

    # ==================================================================
    # ETAPA D - EXTENSIÓN PERSONAL (tokens adicionales del lexer)
    # ==================================================================
    def sentencia_leer(self) -> Leer:
        """leer → 'leer' ID ';'"""
        tok = self.coincidir('PR_LEER')
        tok_id = self.coincidir('ID')
        self.coincidir(';')
        return Leer(tok_id.valor, tok.linea)

    def sentencia_parar(self) -> Parar:
        """parar → 'parar' ';'"""
        tok = self.coincidir('PR_PARAR')
        self.coincidir(';')
        return Parar(tok.linea)

    def sentencia_continuar(self) -> Continuar:
        """continuar → 'continuar' ';'"""
        tok = self.coincidir('PR_CONTINUAR')
        self.coincidir(';')
        return Continuar(tok.linea)

    def sentencia_funcion(self) -> Funcion:
        """funcion → 'funcion' tipo ID '(' parametros? ')' bloque"""
        tok = self.coincidir('PR_FUNCION')
        if not self.es(*TIPOS_DATO):
            self.error('se esperaba el tipo de retorno de la funcion')
        tipo_retorno = self.token_actual.valor
        self.avanzar()
        nombre = self.coincidir('ID').valor
        self.coincidir('(')
        parametros: List[Parametro] = []
        if not self.es(')'):
            parametros.append(self.parametro())
            while self.es(','):
                self.coincidir(',')
                parametros.append(self.parametro())
        self.coincidir(')')
        cuerpo = self.bloque()
        return Funcion(tipo_retorno, nombre, parametros, cuerpo, tok.linea)

    def parametro(self) -> Parametro:
        """parametro → tipo ID"""
        if not self.es(*TIPOS_DATO):
            self.error('se esperaba el tipo del parametro')
        tipo = self.token_actual.valor
        self.avanzar()
        return Parametro(tipo, self.coincidir('ID').valor)

    def sentencia_retornar(self) -> Retornar:
        """retornar → 'retornar' expresion? ';'"""
        tok = self.coincidir('PR_RETORNAR')
        expr: Optional[NodoAST] = None
        if not self.es(';'):
            expr = self.expresion()
        self.coincidir(';')
        return Retornar(expr, tok.linea)

    def llamada_funcion(self) -> LlamadaFuncion:
        """llamada → ID '(' (expresion (',' expresion)*)? ')'"""
        tok = self.coincidir('ID')
        self.coincidir('(')
        argumentos: List[NodoAST] = []
        if not self.es(')'):
            argumentos.append(self.expresion())
            while self.es(','):
                self.coincidir(',')
                argumentos.append(self.expresion())
        self.coincidir(')')
        return LlamadaFuncion(tok.valor, argumentos, tok.linea)

    def sentencia_llamada(self) -> LlamadaFuncion:
        """llamada como sentencia → llamada ';'"""
        nodo = self.llamada_funcion()
        self.coincidir(';')
        return nodo
