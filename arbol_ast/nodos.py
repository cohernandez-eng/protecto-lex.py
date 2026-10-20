"""
==========================================================================
 NODOS DEL AST (ÁRBOL DE SINTAXIS ABSTRACTA)
==========================================================================
 Cada clase es un TIPO DE NODO del árbol que construye el parser.
 Ejemplo:  entero x = 5 + 3;
   Declaracion(tipo='entero', id='x',
               expr=OpBinaria(izq=Numero(5), op='+', der=Numero(3)))

 Los nodos base son los del proyecto del docente. Al final están los
 nodos de mi EXTENSIÓN PERSONAL (Decimal, Cadena, Funcion, Leer, ...).
==========================================================================
"""
from dataclasses import dataclass, field
from typing import List, Optional


class NodoAST:
    pass


# ======================================================================
# NODOS BASE (proporcionados por el docente)
# ======================================================================

@dataclass
class Programa(NodoAST):
    sentencias: List[NodoAST]


@dataclass
class Numero(NodoAST):
    valor: int


@dataclass
class Identificador(NodoAST):
    nombre: str
    linea: int


@dataclass
class Declaracion(NodoAST):
    tipo: str
    id: str
    expr: NodoAST
    linea: int


@dataclass
class Asignacion(NodoAST):
    id: str
    expr: NodoAST
    linea: int


@dataclass
class OpBinaria(NodoAST):
    izq: NodoAST
    op: str
    der: NodoAST


@dataclass
class Imprimir(NodoAST):
    expr: NodoAST


@dataclass
class Si(NodoAST):
    condicion: NodoAST
    bloque_v: List[NodoAST]
    # Extensión PR_SINO: rama falsa. Puede ser una lista de sentencias
    # (sino { ... }) o contener un único Si (sino si ( ... ) { ... }).
    bloque_f: Optional[List[NodoAST]] = None


@dataclass
class Mientras(NodoAST):
    condicion: NodoAST
    bloque: List[NodoAST]


# ======================================================================
# NODOS DE LA EXTENSIÓN PERSONAL
# ======================================================================

@dataclass
class Decimal(NodoAST):
    """Literal NUMERO_DECIMAL, por ejemplo 3.14."""
    valor: float


@dataclass
class Cadena(NodoAST):
    """Literal CADENA_LITERAL, sin las comillas."""
    valor: str


@dataclass
class Booleano(NodoAST):
    """Literal BOOLEANO: verdadero / falso."""
    valor: bool


@dataclass
class OpUnaria(NodoAST):
    """Operadores de un solo operando: 'no' lógico y '-' negativo."""
    op: str
    expr: NodoAST


@dataclass
class Leer(NodoAST):
    """leer ID ;"""
    id: str
    linea: int


@dataclass
class Parar(NodoAST):
    """parar ;  (equivalente a break)"""
    linea: int


@dataclass
class Continuar(NodoAST):
    """continuar ;  (equivalente a continue)"""
    linea: int


@dataclass
class Parametro(NodoAST):
    tipo: str
    nombre: str


@dataclass
class Funcion(NodoAST):
    """funcion tipo ID ( parametros ) bloque"""
    tipo_retorno: str
    nombre: str
    parametros: List[Parametro]
    cuerpo: List[NodoAST]
    linea: int


@dataclass
class Retornar(NodoAST):
    """retornar expresion? ;"""
    expr: Optional[NodoAST]
    linea: int


@dataclass
class LlamadaFuncion(NodoAST):
    """ID ( argumentos ) — como expresión o como sentencia."""
    nombre: str
    argumentos: List[NodoAST] = field(default_factory=list)
    linea: int = 0
