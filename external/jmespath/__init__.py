from external.jmespath import parser

__version__ = "1.0.0"


def compile(
    expression,
):
    return parser.Parser().parse(expression)


def search(
    expression,
    data,
    options=None,
):
    return (
        parser.Parser()
        .parse(expression)
        .search(
            data,
            options=options,
        )
    )
