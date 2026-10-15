import sympy as sp

from engine.evaluator import Evaluator
from engine.scientific import calculate, format_result, parse_expression


def test_simplify_identity():
    assert calculate("sin(x)^2 + cos(x)^2", "Simplify") == 1


def test_calculus_operations():
    assert calculate("x^3", "Differentiate") == 3 * sp.Symbol("x") ** 2
    assert calculate("2*x", "Integrate") == sp.Symbol("x") ** 2


def test_factor_and_solve():
    assert format_result(calculate("x^2 - 4", "Factor")) == "(x - 2)*(x + 2)"
    assert format_result(calculate("x^2 - 4 = 0", "Solve")) == "[-2, 2]"


def test_unknown_names_are_rejected():
    try:
        parse_expression("os.system(x)")
    except ValueError as error:
        assert "Unknown name" in str(error)
    else:
        raise AssertionError("unsafe name was accepted")


def test_reciprocal_trigonometry_is_available():
    evaluator = Evaluator()
    evaluator.angle = "rad"
    assert abs(evaluator.evaluate("cot(pi/4)") - 1) < 1e-12
    assert abs(evaluator.evaluate("sec(0)") - 1) < 1e-12
    assert abs(evaluator.evaluate("csc(pi/2)") - 1) < 1e-12
