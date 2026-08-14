# main.py

from lexer.lexer import Lexer


def main():

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

    print("=" * 60)
    print("COMPILADOR")
    print("=" * 60)

    print("\n[CODIGO FUENTE]")
    print(codigo)

    
    # FASE 1
    

    lexer = Lexer(codigo)
    tokens = lexer.analizar()
    print("[TOKENS]")

    for token in tokens:
        print(token)


if __name__ == "__main__":
    main()