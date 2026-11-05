"""Deterministic arithmetic tests; RSA demo smoke tests live separately."""

from dataclasses import FrozenInstanceError
from math import prod

import pytest

from broadcastguard.math_core import (
    broadcast_attack,
    crt,
    integer_nth_root,
    integer_to_message,
    message_to_integer,
)


def test_starter_small_example() -> None:
    moduli = [55, 391, 1189]
    ciphertexts = [pow(12, 3, n) for n in moduli]
    assert ciphertexts == [23, 164, 539]
    assert crt(ciphertexts, moduli) == (1728, prod(moduli))
    result = broadcast_attack(ciphertexts, moduli)
    assert (result.combined, result.product, result.root, result.exact) == (
        1728, prod(moduli), 12, True
    )
    with pytest.raises(FrozenInstanceError):
        result.root = 13


@pytest.mark.parametrize("message,minimum", [(2, 1), (12, 2), (30, 3)])
@pytest.mark.parametrize("count", [1, 2, 3])
def test_starter_minimum_intercepts(message: int, minimum: int, count: int) -> None:
    moduli = [55, 391, 1189][:count]
    result = broadcast_attack([pow(message, 3, n) for n in moduli], moduli)
    recovered = result.exact and result.root == message
    assert recovered == (count >= minimum)
    assert recovered == (message**3 < prod(moduli))


def test_exact_root_does_not_confirm_plaintext() -> None:
    # 2**3 mod 7 == 1: an exact cube root exists, but it is not M=2.
    result = broadcast_attack([pow(2, 3, 7)], [7])
    assert result.exact
    assert result.root == 1
    assert result.root != 2


@pytest.mark.parametrize("exponent", [2, 3, 5, 17])
@pytest.mark.parametrize("root", [0, 1, 12, 2**1024 + 75])
def test_exact_integer_roots(root: int, exponent: int) -> None:
    assert integer_nth_root(root**exponent, exponent) == (root, True)


@pytest.mark.parametrize("root", [12, 2**1024 + 75])
@pytest.mark.parametrize("exponent", [2, 3, 5])
def test_floor_roots_around_perfect_powers(root: int, exponent: int) -> None:
    assert integer_nth_root(root**exponent - 1, exponent) == (root - 1, False)
    assert integer_nth_root(root**exponent + 1, exponent) == (root, False)


def test_crt_residue_invariants_and_single_modulus() -> None:
    remainders, moduli = [0, 3, 5], [7, 11, 13]
    combined, product = crt(tuple(remainders), tuple(moduli))
    assert product == prod(moduli)
    assert 0 <= combined < product
    assert [combined % n for n in moduli] == remainders
    assert crt([0], [7]) == (0, 7)
    assert crt([6], [7]) == (6, 7)


@pytest.mark.parametrize("remainders,moduli", [
    ([], []), ([1], []), ([], [7]), ([1, 2], [7]),
    ([0], [0]), ([0], [1]), ([0], [-7]),
    ([1, 2], [55, 11]), ([1, 2], [7, 7]),
    ([-1], [7]), ([7], [7]), ([8], [7]),
])
def test_crt_rejects_invalid_values(remainders: list[int], moduli: list[int]) -> None:
    with pytest.raises(ValueError):
        crt(remainders, moduli)
    with pytest.raises(ValueError):
        broadcast_attack(remainders, moduli)


@pytest.mark.parametrize("remainders,moduli", [
    (None, [7]), ([1], None), ("1", [7]), (b"1", [7]),
    ([1.0], [7]), ([True], [7]), ([1], [7.0]), ([1], [True]),
])
def test_crt_rejects_wrong_types(remainders: object, moduli: object) -> None:
    with pytest.raises(TypeError):
        crt(remainders, moduli)


@pytest.mark.parametrize("value,exponent", [(-1, 3), (8, -1), (8, 0), (8, 1)])
def test_root_rejects_invalid_values(value: int, exponent: int) -> None:
    with pytest.raises(ValueError):
        integer_nth_root(value, exponent)


@pytest.mark.parametrize("value,exponent", [(8.0, 3), (True, 3), (8, 3.0), (8, True)])
def test_root_rejects_wrong_types(value: object, exponent: object) -> None:
    with pytest.raises(TypeError):
        integer_nth_root(value, exponent)


@pytest.mark.parametrize("exponent", [-1, 0, 1])
def test_attack_rejects_invalid_exponents(exponent: int) -> None:
    with pytest.raises(ValueError):
        broadcast_attack([1], [7], exponent)


@pytest.mark.parametrize("exponent", [3.0, True, "3", None])
def test_attack_rejects_exponent_types(exponent: object) -> None:
    with pytest.raises(TypeError):
        broadcast_attack([1], [7], exponent)


@pytest.mark.parametrize("data", [b"\x00", b"\x00\x00B", b"hello", "Xin chào".encode(), b"\xff" * 180])
def test_bytes_round_trip(data: bytes) -> None:
    assert integer_to_message(message_to_integer(data), len(data)) == data


def test_empty_message_rejected() -> None:
    with pytest.raises(ValueError):
        message_to_integer(b"")


@pytest.mark.parametrize("data", [None, "hello", [65], 65, bytearray(b"A"), memoryview(b"A")])
def test_message_requires_bytes(data: object) -> None:
    with pytest.raises(TypeError):
        message_to_integer(data)


@pytest.mark.parametrize("value,length", [(-1, 1), (0, 0), (1, -1), (256, 1)])
def test_encoding_rejects_invalid_values(value: int, length: int) -> None:
    with pytest.raises(ValueError):
        integer_to_message(value, length)


@pytest.mark.parametrize("value,length", [(1.0, 1), (True, 1), (1, 1.0), (1, True), (None, 1)])
def test_encoding_rejects_wrong_types(value: object, length: object) -> None:
    with pytest.raises(TypeError):
        integer_to_message(value, length)


def test_encoding_boundaries() -> None:
    assert integer_to_message(0, 1) == b"\x00"
    assert integer_to_message(255, 1) == b"\xff"
