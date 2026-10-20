# Entrega 1 — Lexer

## Objetivo

Completar el **Lexer** proporcionado por el catedrático.

## Implementación

Implementar los siguientes tokens:

- `PR_SI`
- `PR_MIENTRAS`
- `PR_IMPRIMIR`
- `OP_REL`
- Tokens adicionales propuestos en la tarea anterior.

## Operadores relacionales

`OP_REL` debe reconocer los siguientes operadores:

- `==`
- `!=`
- `<`
- `>`
- `<=`
- `>=`

## Prueba

El Lexer debe procesar correctamente el siguiente código en `main.py`:

```python
codigo = """
entero x = 10;
entero limite = 20;

mientras (x <= limite) {
    si (x != 15) {
        imprimir x;
    }
    x = x + 2;
}
"""
