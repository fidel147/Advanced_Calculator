from engine.number_theory import (
    divisors,
    factorize,
    fibonacci,
    gcd,
    is_prime,
    lcm,
    modular_inverse,
    modular_power,
    totient,
)


def test_integer_number_theory():
    assert is_prime(97)
    assert not is_prime(91)
    assert factorize(360) == {2: 3, 3: 2, 5: 1}
    assert gcd(48, 18) == 6
    assert lcm(12, 18) == 36
    assert modular_inverse(3, 11) == 4
    assert modular_power(2, 10, 1000) == 24
    assert fibonacci(10) == 55
    assert divisors(12) == [1, 2, 3, 4, 6, 12]
    assert totient(9) == 6
