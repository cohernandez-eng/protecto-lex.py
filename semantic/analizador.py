"""
==========================================================================
 FASE 3 DEL COMPILADOR: ANALIZADOR SEMÁNTICO
==========================================================================
 Autor: Celso Otoniel Hernández - Carné 2400455
 Curso: Compiladores - USPG

 ¿QUÉ HACE ESTE ARCHIVO?
   Recorre el AST que construyó el parser (parser/parser.py) y revisa que
   el programa TENGA SENTIDO, no solo que esté bien escrito:
     - no usar una variable sin declararla,
     - no declarar dos veces la misma variable,
     - que los tipos coincidan (no sumar un número con 'verdadero'),
     - que las condiciones de si / mientras sean booleanas.
   NO ejecuta el programa: solo revisa estructura y tipos.

 ¿CÓMO LO HACE? (patrón VISITOR)
   analizar(nodo) busca el método visitar_<NombreDelNodo> y lo llama.
     - Las EXPRESIONES devuelven su tipo: 'entero', 'decimal', 'cadena'
       o 'booleano'.
     - Las SENTENCIAS devuelven None.
   Si un nodo no tiene visitante, error_generico() avisa que falta.

 TABLA DE SÍMBOLOS
   self.tabla_simbolos  = {nombre_variable: tipo}     (una sola, GLOBAL)
   self.tabla_funciones = {nombre: (tipo_retorno, [tipos de parámetros])}
                          [EXTENSIÓN: funciones]

 ¿QUÉ ES MÍO?
   - TODO 1, 2, 3, 5 y 6 del docente (el TODO 4, OpBinaria, lo dejó
     resuelto el docente y yo lo amplié).
   - Las reglas de mi EXTENSIÓN PERSONAL, marcadas con [EXTENSIÓN].

 TIPOS DE ERROR (los mismos que espera main.py):
   NameError  -> variable o función no declarada, o declarada dos veces.
   TypeError  -> tipos incompatibles.
   ValueError -> instrucción fuera de su lugar (parar fuera de un ciclo,
                 retornar fuera de una función) [EXTENSIÓN].
==========================================================================
"""
from typing import Dict, List, Optional, Tuple
from arbol_ast.nodos import (
    NodoAST, Programa, Declaracion, Asignacion, Numero, Identificador,
    OpBinaria, Imprimir, Si, Mientras,
    # Nodos de mi extensión personal
    Decimal, Cadena, Booleano, OpUnaria, Leer, Parar, Continuar,
    Funcion, Retornar, LlamadaFuncion,
)

# Operadores agrupados por el tipo de regla que siguen
ARITMETICOS = {'+', '-', '*', '/'}
RELACIONALES = {'<', '>', '<=', '>='}
IGUALDAD = {'==', '!='}
LOGICOS = {'y', 'o'}                 # [EXTENSIÓN]
NUMERICOS = {'entero', 'decimal'}    # [EXTENSIÓN: decimal]


def _linea(nodo: NodoAST) -> str:
    """Texto ' Linea N:' si el nodo conoce su línea (para los mensajes)."""
    linea = getattr(nodo, 'linea', 0)
    return f' Linea {linea}:' if linea else ''


class AnalizadorSemantico:
    def __init__(self):
        # YA IMPLEMENTADO (docente). Ejemplo: {'edad': 'entero'}.
        self.tabla_simbolos: Dict[str, str] = {}
        # [EXTENSIÓN] Tabla aparte para las funciones.
        self.tabla_funciones: Dict[str, Tuple[str, List[str]]] = {}
        # [EXTENSIÓN] Contexto: ¿estoy dentro de un ciclo o de una función?
        self.ciclos_abiertos = 0
        self.funcion_actual: Optional[Funcion] = None

    # ------------------------------------------------------------------
    # Infraestructura (YA IMPLEMENTADA por el docente)
    # ------------------------------------------------------------------
    def analizar(self, nodo: NodoAST) -> Optional[str]:
        # Patrón Visitor: 'Declaracion' -> visitar_Declaracion(nodo)
        metodo = f'visitar_{type(nodo).__name__}'
        visitante = getattr(self, metodo, self.error_generico)
        return visitante(nodo)

    def error_generico(self, nodo: NodoAST):
        # Es intencional: nuevas clases AST requieren un visitante propio.
        raise NotImplementedError(
            f'Falta soporte semantico para el nodo {type(nodo).__name__}. '
            'Si agregaste nodos AST por tus tokens propios, implementa su visitante.'
        )

    def visitar_Programa(self, nodo: Programa) -> None:
        for sentencia in nodo.sentencias:
            self.analizar(sentencia)

    def visitar_Numero(self, nodo: Numero) -> str:
        return 'entero'

    def visitar_Imprimir(self, nodo: Imprimir) -> None:
        # Se analiza la expresión para descubrir variables inexistentes.
        self.analizar(nodo.expr)

    # ------------------------------------------------------------------
    # Auxiliares propios
    # ------------------------------------------------------------------
    @staticmethod
    def compatible(tipo_variable: str, tipo_valor: str) -> bool:
        """¿Se puede guardar un valor de tipo_valor en una variable de tipo_variable?

        Regla base: deben ser iguales.
        [EXTENSIÓN] Ampliación numérica: un entero cabe en un decimal
        (decimal x = 5;), pero un decimal NO cabe en un entero
        (entero x = 2.5; es error, se perdería la parte decimal).
        """
        return tipo_variable == tipo_valor or (
            tipo_variable == 'decimal' and tipo_valor == 'entero')

    def visitar_bloque(self, sentencias: List[NodoAST]) -> None:
        """Visita cada sentencia de un bloque, sin ejecutarlo."""
        for sentencia in sentencias:
            self.analizar(sentencia)

    def exigir_booleano(self, condicion: NodoAST, instruccion: str, nodo: NodoAST) -> None:
        """La condición de si / mientras debe ser de tipo booleano."""
        tipo = self.analizar(condicion)
        if tipo != 'booleano':
            raise TypeError(
                f"[Error Semantico]{_linea(nodo)} la condicion de '{instruccion}' "
                f"debe ser booleana, se recibio '{tipo}'."
            )

    # ==================================================================
    # TODO 1 - DECLARACIÓN
    # ==================================================================
    def visitar_Declaracion(self, nodo: Declaracion) -> None:
        # 1) No puede existir ya una variable (ni función) con ese nombre.
        if nodo.id in self.tabla_simbolos or nodo.id in self.tabla_funciones:
            raise NameError(
                f"[Error Semantico] Linea {nodo.linea}: la variable "
                f"'{nodo.id}' ya fue declarada."
            )
        # 2) Se analiza la expresión ANTES de registrar la variable:
        #    así 'entero x = x + 1;' detecta que x todavía no existe.
        tipo_expr = self.analizar(nodo.expr)
        # 3) El tipo de la expresión debe ser compatible con el declarado.
        if not self.compatible(nodo.tipo, tipo_expr):
            raise TypeError(
                f"[Error Semantico] Linea {nodo.linea}: no se puede inicializar "
                f"'{nodo.id}' ({nodo.tipo}) con un valor de tipo '{tipo_expr}'."
            )
        # 4) Recién ahora se registra en la tabla de símbolos.
        self.tabla_simbolos[nodo.id] = nodo.tipo

    # ==================================================================
    # TODO 2 - ASIGNACIÓN
    # ==================================================================
    def visitar_Asignacion(self, nodo: Asignacion) -> None:
        # 1) La variable debe estar declarada.
        if nodo.id not in self.tabla_simbolos:
            raise NameError(
                f"[Error Semantico] Linea {nodo.linea}: se asigna a "
                f"'{nodo.id}', que no ha sido declarada."
            )
        # 2) El valor debe ser compatible con el tipo guardado.
        tipo_variable = self.tabla_simbolos[nodo.id]
        tipo_expr = self.analizar(nodo.expr)
        if not self.compatible(tipo_variable, tipo_expr):
            raise TypeError(
                f"[Error Semantico] Linea {nodo.linea}: no se puede asignar un "
                f"valor '{tipo_expr}' a '{nodo.id}' ({tipo_variable})."
            )

    # ==================================================================
    # TODO 3 - IDENTIFICADOR
    # ==================================================================
    def visitar_Identificador(self, nodo: Identificador) -> str:
        if nodo.nombre not in self.tabla_simbolos:
            raise NameError(
                f"[Error Semantico] Linea {nodo.linea}: la variable "
                f"'{nodo.nombre}' no ha sido declarada."
            )
        return self.tabla_simbolos[nodo.nombre]

    # ==================================================================
    # TODO 4 - OPERACIÓN BINARIA (base del docente, AMPLIADA por mí)
    # ==================================================================
    def visitar_OpBinaria(self, nodo: OpBinaria) -> str:
        tipo_izq = self.analizar(nodo.izq)
        tipo_der = self.analizar(nodo.der)
        op = nodo.op

        # + - * /  -> números. Base: entero op entero = entero.
        # [EXTENSIÓN] si alguno es decimal, el resultado es decimal.
        # [EXTENSIÓN] cadena + cadena = cadena (concatenar texto).
        if op in ARITMETICOS:
            if tipo_izq in NUMERICOS and tipo_der in NUMERICOS:
                return 'decimal' if 'decimal' in (tipo_izq, tipo_der) else 'entero'
            if op == '+' and tipo_izq == tipo_der == 'cadena':
                return 'cadena'
            raise TypeError(
                f"[Error Semantico]{_linea(nodo)} el operador '{op}' exige dos "
                f"numeros, se recibieron '{tipo_izq}' y '{tipo_der}'."
            )

        # < > <= >=  -> dos números, resultado booleano.
        # Por eso '1 < x < 5' es error: (1 < x) es booleano.
        if op in RELACIONALES:
            if tipo_izq in NUMERICOS and tipo_der in NUMERICOS:
                return 'booleano'
            raise TypeError(
                f"[Error Semantico]{_linea(nodo)} el operador '{op}' exige dos "
                f"numeros, se recibieron '{tipo_izq}' y '{tipo_der}'."
            )

        # == !=  -> dos números (base).
        # [EXTENSIÓN] también dos cadenas o dos booleanos del mismo tipo.
        if op in IGUALDAD:
            if (tipo_izq in NUMERICOS and tipo_der in NUMERICOS) or (
                    tipo_izq == tipo_der and tipo_izq in ('cadena', 'booleano')):
                return 'booleano'
            raise TypeError(
                f"[Error Semantico]{_linea(nodo)} no se pueden comparar con '{op}' "
                f"valores '{tipo_izq}' y '{tipo_der}'."
            )

        # [EXTENSIÓN] y / o -> dos booleanos, resultado booleano.
        if op in LOGICOS:
            if tipo_izq == tipo_der == 'booleano':
                return 'booleano'
            raise TypeError(
                f"[Error Semantico]{_linea(nodo)} el operador logico '{op}' exige "
                f"dos booleanos, se recibieron '{tipo_izq}' y '{tipo_der}'."
            )

        raise TypeError(
            f"[Error Semantico] Operador '{op}' sin regla semantica. "
            'Si es una extension personal, define su validacion y tipo de resultado.'
        )

    # ==================================================================
    # TODO 5 - SI  (con la rama 'sino' de mi extensión)
    # ==================================================================
    def visitar_Si(self, nodo: Si) -> None:
        self.exigir_booleano(nodo.condicion, 'si', nodo)
        self.visitar_bloque(nodo.bloque_v)
        # [EXTENSIÓN] La rama 'sino' también se revisa (sin ejecutarla).
        # Un 'sino si' llega aquí como otro nodo Si dentro de bloque_f.
        if nodo.bloque_f is not None:
            self.visitar_bloque(nodo.bloque_f)

    # ==================================================================
    # TODO 6 - MIENTRAS
    # ==================================================================
    def visitar_Mientras(self, nodo: Mientras) -> None:
        self.exigir_booleano(nodo.condicion, 'mientras', nodo)
        # [EXTENSIÓN] Se marca que estamos dentro de un ciclo para que
        # 'parar' y 'continuar' sean válidos aquí adentro.
        self.ciclos_abiertos += 1
        try:
            self.visitar_bloque(nodo.bloque)
        finally:
            self.ciclos_abiertos -= 1

    # ==================================================================
    # [EXTENSIÓN PERSONAL] Literales nuevos: devuelven su tipo
    # ==================================================================
    def visitar_Decimal(self, nodo: Decimal) -> str:
        return 'decimal'

    def visitar_Cadena(self, nodo: Cadena) -> str:
        return 'cadena'

    def visitar_Booleano(self, nodo: Booleano) -> str:
        return 'booleano'

    # ==================================================================
    # [EXTENSIÓN PERSONAL] Operadores unarios: 'no' y '-'
    # ==================================================================
    def visitar_OpUnaria(self, nodo: OpUnaria) -> str:
        tipo = self.analizar(nodo.expr)
        if nodo.op == 'no':
            if tipo != 'booleano':
                raise TypeError(
                    f"[Error Semantico]{_linea(nodo)} el operador 'no' exige un "
                    f"booleano, se recibio '{tipo}'."
                )
            return 'booleano'
        if nodo.op == '-':
            if tipo not in NUMERICOS:
                raise TypeError(
                    f"[Error Semantico]{_linea(nodo)} el '-' unario exige un "
                    f"numero, se recibio '{tipo}'."
                )
            return tipo
        raise TypeError(f"[Error Semantico] Operador unario '{nodo.op}' sin regla semantica.")

    # ==================================================================
    # [EXTENSIÓN PERSONAL] leer, parar, continuar
    # ==================================================================
    def visitar_Leer(self, nodo: Leer) -> None:
        # Solo se revisa que la variable exista; no se lee del teclado.
        if nodo.id not in self.tabla_simbolos:
            raise NameError(
                f"[Error Semantico] Linea {nodo.linea}: 'leer' usa '{nodo.id}', "
                "que no ha sido declarada."
            )

    def visitar_Parar(self, nodo: Parar) -> None:
        if self.ciclos_abiertos == 0:
            raise ValueError(
                f"[Error Semantico] Linea {nodo.linea}: 'parar' solo puede usarse "
                "dentro de un ciclo 'mientras'."
            )

    def visitar_Continuar(self, nodo: Continuar) -> None:
        if self.ciclos_abiertos == 0:
            raise ValueError(
                f"[Error Semantico] Linea {nodo.linea}: 'continuar' solo puede usarse "
                "dentro de un ciclo 'mientras'."
            )

    # ==================================================================
    # [EXTENSIÓN PERSONAL] Funciones
    # ==================================================================
    def visitar_Funcion(self, nodo: Funcion) -> None:
        # 1) El nombre no puede repetirse (ni con otra función ni con una variable).
        if nodo.nombre in self.tabla_funciones or nodo.nombre in self.tabla_simbolos:
            raise NameError(
                f"[Error Semantico] Linea {nodo.linea}: el nombre '{nodo.nombre}' "
                "ya fue declarado."
            )
        # 2) Parámetros sin nombres repetidos.
        nombres = [p.nombre for p in nodo.parametros]
        repetidos = {n for n in nombres if nombres.count(n) > 1}
        if repetidos:
            raise NameError(
                f"[Error Semantico] Linea {nodo.linea}: parametro repetido "
                f"'{sorted(repetidos)[0]}' en la funcion '{nodo.nombre}'."
            )
        # 3) Se registra ANTES de revisar el cuerpo, para permitir recursión.
        self.tabla_funciones[nodo.nombre] = (nodo.tipo_retorno, [p.tipo for p in nodo.parametros])

        # 4) Los parámetros solo existen dentro del cuerpo: se guarda la tabla
        #    global, se agregan los parámetros y al terminar se restaura.
        #    (Única excepción a la tabla global de esta entrega.)
        tabla_global = dict(self.tabla_simbolos)
        funcion_anterior, ciclos_anteriores = self.funcion_actual, self.ciclos_abiertos
        try:
            for p in nodo.parametros:
                self.tabla_simbolos[p.nombre] = p.tipo
            self.funcion_actual, self.ciclos_abiertos = nodo, 0
            self.visitar_bloque(nodo.cuerpo)
        finally:
            self.tabla_simbolos = tabla_global
            self.funcion_actual, self.ciclos_abiertos = funcion_anterior, ciclos_anteriores

    def visitar_Retornar(self, nodo: Retornar) -> None:
        if self.funcion_actual is None:
            raise ValueError(
                f"[Error Semantico] Linea {nodo.linea}: 'retornar' solo puede usarse "
                "dentro de una funcion."
            )
        esperado = self.funcion_actual.tipo_retorno
        if nodo.expr is None:
            raise TypeError(
                f"[Error Semantico] Linea {nodo.linea}: la funcion "
                f"'{self.funcion_actual.nombre}' debe retornar un valor '{esperado}'."
            )
        tipo = self.analizar(nodo.expr)
        if not self.compatible(esperado, tipo):
            raise TypeError(
                f"[Error Semantico] Linea {nodo.linea}: la funcion "
                f"'{self.funcion_actual.nombre}' retorna '{esperado}', "
                f"pero se retorna un valor '{tipo}'."
            )

    def visitar_LlamadaFuncion(self, nodo: LlamadaFuncion) -> str:
        if nodo.nombre not in self.tabla_funciones:
            raise NameError(
                f"[Error Semantico] Linea {nodo.linea}: la funcion "
                f"'{nodo.nombre}' no ha sido declarada."
            )
        tipo_retorno, tipos_param = self.tabla_funciones[nodo.nombre]
        if len(nodo.argumentos) != len(tipos_param):
            raise TypeError(
                f"[Error Semantico] Linea {nodo.linea}: '{nodo.nombre}' espera "
                f"{len(tipos_param)} argumento(s) y recibio {len(nodo.argumentos)}."
            )
        for i, (arg, esperado) in enumerate(zip(nodo.argumentos, tipos_param), start=1):
            tipo = self.analizar(arg)
            if not self.compatible(esperado, tipo):
                raise TypeError(
                    f"[Error Semantico] Linea {nodo.linea}: el argumento {i} de "
                    f"'{nodo.nombre}' debe ser '{esperado}', se recibio '{tipo}'."
                )
        return tipo_retorno
