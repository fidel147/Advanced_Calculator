import numpy as np

from engine.matrix import calculate, format_result, parse_matrix


def test_matrix_operations():
    assert np.array_equal(calculate("Add", "1 2; 3 4", "4 3; 2 1"), [[5, 5], [5, 5]])
    assert np.array_equal(calculate("Multiply", "1 2; 3 4", "4 3; 2 1"), [[8, 5], [20, 13]])
    assert format_result(calculate("Determinant A", "1 2; 3 4")) == "-2"


def test_vectors_and_linear_systems():
    assert format_result(calculate("Dot product", "1 2 3", "4 5 6")) == "32"
    solution = calculate("Solve A x = b", "2 0; 0 4", "4; 8")
    assert np.allclose(solution, [2, 2])


def test_matrix_shape_validation():
    try:
        parse_matrix("1 2; 3")
    except ValueError as error:
        assert "same number" in str(error)
    else:
        raise AssertionError("ragged matrix was accepted")
