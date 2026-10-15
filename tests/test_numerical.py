from engine.numerical import bisection, differentiate, integrate, interpolate, newton


def test_root_methods_converge():
    expected = 2 ** 0.5
    for result in (bisection("x^2 - 2", 0, 2), newton("x^2 - 2", 1)):
        assert result.converged
        assert abs(result.value - expected) < 1e-6
        assert result.residual < 1e-6


def test_calculus_and_interpolation():
    assert abs(integrate("x^2", 0, 1).value - 1 / 3) < 1e-8
    assert abs(differentiate("x^3", 2).value - 12) < 1e-4
    assert interpolate([0, 1, 2], [0, 2, 4], 1.5) == 3
