"""Integer number-theory operations with bounded, validated inputs."""

import math


def integer(value):
    number = int(value)
    if number != float(value):
        raise ValueError("Enter a whole number")
    if abs(number) > 10**12:
        raise ValueError("Number is too large for this workspace")
    return number


def is_prime(value):
    number = integer(value)
    if number < 2:
        return False
    if number % 2 == 0:
        return number == 2
    divisor = 3
    while divisor * divisor <= number:
        if number % divisor == 0:
            return False
        divisor += 2
    return True


def factorize(value):
    number = abs(integer(value))
    if number < 2:
        return {number: 1}
    factors = {}
    divisor = 2
    while divisor * divisor <= number:
        while number % divisor == 0:
            factors[divisor] = factors.get(divisor, 0) + 1
            number //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if number > 1:
        factors[number] = factors.get(number, 0) + 1
    return factors


def gcd(first, second):
    return math.gcd(integer(first), integer(second))


def lcm(first, second):
    return math.lcm(integer(first), integer(second))


def modular_inverse(value, modulus):
    return pow(integer(value), -1, integer(modulus))


def modular_power(base, exponent, modulus):
    return pow(integer(base), integer(exponent), integer(modulus))


def fibonacci(index):
    index = integer(index)
    if index < 0 or index > 10000:
        raise ValueError("Index must be between 0 and 10000")
    first, second = 0, 1
    for _ in range(index):
        first, second = second, first + second
    return first


def divisors(value):
    number = abs(integer(value))
    if number == 0:
        raise ValueError("Zero has infinitely many divisors")
    small, large = [], []
    divisor = 1
    while divisor * divisor <= number:
        if number % divisor == 0:
            small.append(divisor)
            if divisor * divisor != number:
                large.append(number // divisor)
        divisor += 1
    return small + large[::-1]


def totient(value):
    number = abs(integer(value))
    if number < 1:
        raise ValueError("Totient needs a positive integer")
    result = number
    for prime in factorize(number):
        result -= result // prime
    return result
