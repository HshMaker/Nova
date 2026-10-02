import re

TOKEN_SPEC = [
    ("COMMENT", r"//.*"),
    ("STRING", r'"[^"]*"'),
    ("NUMBER", r"\d+\.\d+|\d+"),
    ("LBRACKET", r"\["),
    ("RBRACKET", r"\]"),
    ("IDENT", r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("ELLIPSIS", r"\.\.\."),
    ("DOT", r"\."),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("LBRACE", r"\{"),
    ("RBRACE", r"\}"),
    ("COMMA", r","),
    ("COLON", r":"),
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t]+"),
    ("PLUS", r"\+"),  # 연산자
    ("MINUS", r"-"),
    ("STAR", r"\*"),
    ("SLASH", r"/"),
    ("MOD", r"%"),

    ("EQEQ", r"=="),
    ("NOTEQ", r"!="),

    ("GTE", r">="),
    ("LTE", r"<="),
    ("GT", r">"),
    ("LT", r"<"),
    ("AND", r"&&"),
    ("OR", r"\|\|"),
    ("NOT", r"!"),  # 여기까지
    ("ASSIGN", r"\="),
    ("HASH", r"#"),
]

KEYWORDS = {
    "var": "VAR",
    "true": "BOOLEAN",
    "false": "BOOLEAN",

    "repeat": "REPEAT",
    "next": "NEXT",
    "out": "OUT",

    "fun": "FUN",
    "return": "RETURN",

    "if": "IF",
    "then": "THEN",
    "end": "END",
    "other": "OTHER",
    "and": "AND",
    "or": "OR",
    "not": "NOT",

    "take": "TAKE",
    "at": "AT",
    "send": "SEND",

    "pack": "PACK",
}


def tokenize(source):

    tokens = []

    while source:

        matched = False

        for (token_type, pattern) in TOKEN_SPEC:

            match = re.match(pattern, source)

            if match:
                matched_text = match.group(0)
                value = matched_text

                if (token_type != "COMMENT"):
                    if token_type not in (
                        "SKIP",
                        "NEWLINE"
                    ):
                        if (token_type == "IDENT"):
                            token_type = KEYWORDS.get(value, "IDENT")

                        if (token_type == "STRING"):
                            value = value.replace("\\n", "\n")
                        tokens.append(
                            (token_type, value)
                        )

                source = source[len(matched_text):]
                matched = True
                break

        if not matched:
            raise SyntaxError(
                f"Unexpected character: {source[0]}"
            )

    return tokens
