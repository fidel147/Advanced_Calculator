"""Numerical analysis algorithms with convergence and error reporting."""

from dataclasses import dataclass

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq

from engine.scientific import parse_expression


@dataclass
class NumericalResult:
    value: float
    iterations: int
    residual: float
    converged: bool
    history: tuple = ()


def function(expression, variable="x"):
    """Compile a validated SymPy expression into a real-valued numeric function."""
    parsed = parse_expression(expression)
    symbol = parsed.free_symbols
    if len(symbol) > 1:
        raise ValueError("Numerical methods support one variable at a time")
    selected = next((item for item in symbol if item.name == variable), None)
    if selected is None:
        raise ValueError(f"Expression must use variable {variable}")
    import sympy as sp
    compiled = sp.lambdify(selected, parsed, modules=["numpy", "math"])

    def evaluate(value):
        result = compiled(value)
        if np.iscomplexobj(result) or not np.isfinite(result):
            raise ValueError("Function is not finite and real at this point")
        return float(result)

    return evaluate


def _check_tolerance(tolerance, max_iterations):
    if tolerance <= 0 or max_iterations < 1:
        raise ValueError("Tolerance must be positive and iterations must be at least 1")


def bisection(expression, left, right, tolerance=1e-8, max_iterations=100):
    _check_tolerance(tolerance, max_iterations)
    evaluate = function(expression)
    left, right = float(left), float(right)
    f_left, f_right = evaluate(left), evaluate(right)
    if f_left == 0:
        return NumericalResult(left, 0, 0.0, True, (left,))
    if f_left * f_right > 0:
        raise ValueError("The interval must bracket a sign change")
    history = []
    for iteration in range(1, max_iterations + 1):
        middle = (left + right) / 2
        residual = abs(evaluate(middle))
        history.append(middle)
        if residual <= tolerance or abs(right - left) <= tolerance:
            return NumericalResult(middle, iteration, residual, True, tuple(history))
        if f_left * evaluate(middle) <= 0:
            right = middle
        else:
            left, f_left = middle, evaluate(middle)
    return NumericalResult(middle, max_iterations, residual, False, tuple(history))


def newton(expression, start, tolerance=1e-8, max_iterations=100):
    _check_tolerance(tolerance, max_iterations)
    evaluate = function(expression)
    current = float(start)
    history = []
    for iteration in range(1, max_iterations + 1):
        value = evaluate(current)
        step = max(1e-6, abs(current) * 1e-6)
        slope = (evaluate(current + step) - evaluate(current - step)) / (2 * step)
        if abs(slope) < 1e-14:
            raise ValueError("Derivative is too close to zero")
        next_value = current - value / slope
        history.append(next_value)
        residual = abs(evaluate(next_value))
        if residual <= tolerance or abs(next_value - current) <= tolerance:
            return NumericalResult(next_value, iteration, residual, True, tuple(history))
        current = next_value
    return NumericalResult(current, max_iterations, abs(evaluate(current)), False, tuple(history))


def secant(expression, first, second, tolerance=1e-8, max_iterations=100):
    _check_tolerance(tolerance, max_iterations)
    evaluate = function(expression)
    first, second = float(first), float(second)
    history = [first, second]
    for iteration in range(1, max_iterations + 1):
        f_first, f_second = evaluate(first), evaluate(second)
        denominator = f_second - f_first
        if abs(denominator) < 1e-14:
            raise ValueError("Secant slope is too close to zero")
        next_value = second - f_second * (second - first) / denominator
        history.append(next_value)
        residual = abs(evaluate(next_value))
        if residual <= tolerance or abs(next_value - second) <= tolerance:
            return NumericalResult(next_value, iteration, residual, True, tuple(history))
        first, second = second, next_value
    return NumericalResult(second, max_iterations, abs(evaluate(second)), False, tuple(history))


def brent(expression, left, right, tolerance=1e-8, max_iterations=100):
    _check_tolerance(tolerance, max_iterations)
    evaluate = function(expression)
    value, result = brentq(evaluate, float(left), float(right), xtol=tolerance,
                           maxiter=max_iterations, full_output=True)
    return NumericalResult(float(value), int(result.iterations), abs(evaluate(value)), result.converged, ())


def integrate(expression, left, right):
    evaluate = function(expression)
    value, error = quad(evaluate, float(left), float(right))
    return NumericalResult(float(value), 0, float(error), True, ())


def differentiate(expression, point, step=1e-5):
    if step <= 0:
        raise ValueError("Step must be positive")
    evaluate = function(expression)
    point = float(point)
    value = (evaluate(point + step) - evaluate(point - step)) / (2 * step)
    return NumericalResult(float(value), 1, float(step), True, ())


def interpolate(x_values, y_values, point):
    x_values, y_values = np.asarray(x_values, dtype=float), np.asarray(y_values, dtype=float)
    if len(x_values) != len(y_values) or len(x_values) < 2:
        raise ValueError("Interpolation needs equally sized x/y data with at least two points")
    if len(np.unique(x_values)) != len(x_values):
        raise ValueError("Interpolation x values must be unique")
    return float(np.interp(float(point), x_values, y_values))
