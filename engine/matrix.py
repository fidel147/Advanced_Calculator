"""Validated matrix and vector operations for the scientific workspace."""

import numpy as np


OPERATIONS = (
    "Add", "Subtract", "Multiply", "Transpose A", "Inverse A", "Determinant A",
    "Rank A", "Trace A", "Eigenvalues A", "Solve A x = b", "Dot product", "Cross product",
    "Norm A",
)


def parse_matrix(text):
    """Parse rows separated by semicolons/newlines and values by commas/spaces."""
    rows = [row.strip() for row in text.replace("\n", ";").split(";") if row.strip()]
    if not rows:
        raise ValueError("Enter at least one matrix row")
    values = [[float(value) for value in row.replace(",", " ").split()] for row in rows]
    width = len(values[0])
    if width == 0 or any(len(row) != width for row in values):
        raise ValueError("Every matrix row must have the same number of values")
    return np.asarray(values, dtype=float)


def _vector(matrix, name):
    if matrix.ndim != 2 or 1 not in matrix.shape:
        raise ValueError(f"{name} must be a row or column vector")
    return matrix.reshape(-1)


def calculate(operation, left_text, right_text=""):
    """Run a checked matrix/vector operation and return a numpy result."""
    left = parse_matrix(left_text)
    right = parse_matrix(right_text) if right_text.strip() else None
    if operation == "Add":
        return left + _required(right, "B")
    if operation == "Subtract":
        return left - _required(right, "B")
    if operation == "Multiply":
        return left @ _required(right, "B")
    if operation == "Transpose A":
        return left.T
    if operation == "Inverse A":
        return np.linalg.inv(left)
    if operation == "Determinant A":
        return np.linalg.det(left)
    if operation == "Rank A":
        return np.linalg.matrix_rank(left)
    if operation == "Trace A":
        return np.trace(left)
    if operation == "Eigenvalues A":
        return np.linalg.eigvals(left)
    if operation == "Solve A x = b":
        return np.linalg.solve(left, _required(right, "b").reshape(-1))
    if operation == "Dot product":
        return np.dot(_vector(left, "A"), _vector(_required(right, "B"), "B"))
    if operation == "Cross product":
        return np.cross(_vector(left, "A"), _vector(_required(right, "B"), "B"))
    if operation == "Norm A":
        return np.linalg.norm(left)
    raise ValueError(f"Unknown matrix operation: {operation}")


def _required(value, name):
    if value is None:
        raise ValueError(f"Enter matrix {name}")
    return value


def format_result(value):
    """Format scalars, vectors, and matrices for a result panel."""
    array = np.asarray(value)
    if array.ndim == 0:
        return f"{float(array):.10g}"
    return np.array2string(array, precision=6, suppress_small=True)
