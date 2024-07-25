import ast
import typing


def adjust_source_lineno(
    source: str,
    name: str,
    lineno: int,
) -> typing.Any:
    node = compile(
        source,
        name,
        "exec",
        ast.PyCF_ONLY_AST,
    )
    ast.increment_lineno(
        node,
        lineno,
    )
    return node
