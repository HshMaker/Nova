import sys

from nova.lexer import tokenize
from nova.parser import Parser
from nova.interpreter import Interpreter


def run(filename):

    with open(
        filename,
        "r",
        encoding="utf-8"
    ) as f:

        source = f.read()

    tokens = tokenize(source)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.execute(ast)


def main():
    if (len(sys.argv) != 2):
        print("Usage: nova file.nova")
        exit()

    run(sys.argv[1])


if __name__ == "__main__":
    main()
