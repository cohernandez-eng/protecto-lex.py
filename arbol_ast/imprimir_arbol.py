"""Muestra el AST como árbol de texto (solo presentación, no modifica el AST)."""
from dataclasses import fields, is_dataclass

# Campos que no aportan a la lectura del árbol.
_OCULTOS = {'linea'}


def _es_hoja(valor) -> bool:
    return not is_dataclass(valor) and not isinstance(valor, list)


def _etiqueta(nodo) -> str:
    """Nombre del nodo + sus atributos simples, p. ej. Declaracion(entero edad)."""
    simples = [
        f.name for f in fields(nodo)
        if f.name not in _OCULTOS and _es_hoja(getattr(nodo, f.name))
        and getattr(nodo, f.name) is not None
    ]
    if not simples:
        return type(nodo).__name__
    partes = []
    for nombre in simples:
        valor = getattr(nodo, nombre)
        partes.append(repr(valor) if isinstance(valor, str) and nombre == 'valor' else str(valor))
    return f"{type(nodo).__name__}({' '.join(partes)})"


def _hijos(nodo):
    """Pares (nombre, valor) de los campos que son nodos o listas."""
    for f in fields(nodo):
        valor = getattr(nodo, f.name)
        if is_dataclass(valor) or isinstance(valor, list):
            yield f.name, valor


def arbol_texto(nodo, prefijo: str = '', es_ultimo: bool = True, raiz: bool = True) -> str:
    lineas = []
    conector = '' if raiz else ('└── ' if es_ultimo else '├── ')
    lineas.append(prefijo + conector + _etiqueta(nodo))
    prefijo_hijo = prefijo + ('' if raiz else ('    ' if es_ultimo else '│   '))

    hijos = list(_hijos(nodo))
    for i, (nombre, valor) in enumerate(hijos):
        ultimo = i == len(hijos) - 1
        if isinstance(valor, list):
            # Una lista se muestra como una rama con nombre (p. ej. bloque_v).
            con = '└── ' if ultimo else '├── '
            lineas.append(prefijo_hijo + con + f'[{nombre}]' + (' (vacio)' if not valor else ''))
            sub = prefijo_hijo + ('    ' if ultimo else '│   ')
            for j, elem in enumerate(valor):
                lineas.append(arbol_texto(elem, sub, j == len(valor) - 1, raiz=False))
        else:
            # Nodo con nombre de campo cuando ayuda a leer (izq/der, condicion...).
            sub_txt = arbol_texto(valor, prefijo_hijo, ultimo, raiz=False)
            primera, _, resto = sub_txt.partition('\n')
            con = '└── ' if ultimo else '├── '
            primera = primera.replace(con, con + f'{nombre}: ', 1)
            lineas.append(primera + ('\n' + resto if resto else ''))
    return '\n'.join(lineas)
