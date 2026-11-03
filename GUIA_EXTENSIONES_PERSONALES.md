# Guía de extensiones propias — ¿Qué cambia en la semántica?

**Primero conserva tu lexer, parser y nodos AST del proyecto anterior.** La semántica recorre los NODOS AST, no los tokens directamente. La solución de referencia solo cubre el lenguaje base; nadie conoce de antemano todos los nuevos tokens y tipos de cada estudiante.

| Extensión anterior | ¿Requiere semántica nueva? | Ejemplo de validación |
|---|---|---|
| `%` | Sí, en `visitar_OpBinaria`. | Dos `entero` → `entero`; rechazar booleanos. |
| `^` (potencia) | Sí, en `visitar_OpBinaria`. | Definir operandos y tipo resultante. |
| `&&` / `||` | Sí, en operaciones binarias. | Dos `booleano` → `booleano`. |
| `DECIMAL` | Sí, si el AST preserva el tipo decimal. | `visitar_Decimal` → `decimal`, revisar compatibilidad. |
| `verdadero` / `falso` | Sí, si se añadió nodo `Booleano`. | `visitar_Booleano` → `booleano`; permitir condiciones. |
| `sino` | Sí, para recorrer el bloque alternativo y validar su contenido. | Visitar ambas ramas, no ejecutarlas. |
| `leer(variable)` | Sí, revisar que `variable` exista y sea compatible. | `visitar_Leer`; no leer realmente del teclado. |
| `++` | Sí, cuando actúa sobre variables. | Variable declarada y de tipo numérico. |
| Comentarios `//` ignorados | No, si el lexer los descarta. | No aparecen en el AST. |
| `<=`, `>=` ya representados como `OpBinaria` | No requiere método nuevo. | La versión base ya soporta esos operadores. |

## Ejemplo de `%` incorporado a OpBinaria

Si el estudiante reconoce `10 % 3` como `OpBinaria(Numero(10), '%', Numero(3))`, puede ampliar el conjunto de operadores aritméticos en `visitar_OpBinaria()`. No necesita crear un nodo `Modulo` necesariamente.

## Ejemplo de un nuevo nodo Booleano

```python
# En arbol_ast/nodos.py, si el parser produce este tipo de nodo:
@dataclass
class Booleano(NodoAST):
    valor: bool

# En semantic/analizador.py, se agrega una regla nueva:
def visitar_Booleano(self, nodo: Booleano) -> str:
    return 'booleano'
```

Con este diseño, `si (verdadero) { ... }` puede ser válido si el lexer y parser también lo reconocen. **No basta con cambiar semántica: la extensión debe seguir funcionando en las fases anteriores.**

## Demostraciones mínimas sugeridas

1. Un programa base válido y su tabla de símbolos.
2. Un programa con error semántico base (por ejemplo, variable inexistente).
3. Un programa válido que use la característica personal.
4. Un programa inválido que demuestre su regla semántica (si la extensión llega al AST). En casos como comentarios, documentar por qué no aplica y demostrar que no afectan la semántica.

Documentar para cada variante: token → regla del parser → nodo AST → regla semántica → caso de prueba y resultado esperado.

**Alcance:** todavía NO se ejecutan cálculos, condicionales ni ciclos; se comprueba estructura y coherencia de tipos/declaraciones. No es un intérprete.
