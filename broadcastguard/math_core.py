"""Integer arithmetic for the Textbook RSA attack lab only.

Adapted from BroadcastGuard_Buoc1/broadcast_core.py. No private keys are
accepted here. Textbook RSA must never protect real files or messages.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from math import gcd, prod


@dataclass(frozen=True)
class AttackResult:
    """CRT result and candidate root; exact does not confirm the plaintext.

    exact means only root**exponent == combined. Confirming the original
    plaintext requires a separate comparison in a controlled experiment.
    """

    combined: int
    product: int
    root: int
    exact: bool


def _require_integer(value: object, name: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer (not bool).")


def _require_integer_sequence(values: object, name: str) -> None:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes, bytearray)):
        raise TypeError(f"{name} must be a sequence of integers.")
    for value in values:
        _require_integer(value, name)


def crt(remainders: Sequence[int], moduli: Sequence[int]) -> tuple[int, int]:
    """Return (X, N) with 0 <= X < N and X % n_i == c_i.

    Require nonempty equally sized sequences, moduli > 1, pairwise coprime
    moduli, and canonical remainders 0 <= c_i < n_i. Wrong types raise
    TypeError; invalid values raise ValueError. All arithmetic is integer.
    """
    _require_integer_sequence(remainders, "remainders")
    _require_integer_sequence(moduli, "moduli")
    if not remainders or len(remainders) != len(moduli):
        raise ValueError("At least one matching (ciphertext, modulus) pair is required.")
    if any(n <= 1 for n in moduli):
        raise ValueError("Each modulus must be greater than 1.")
    for i, n_i in enumerate(moduli):
        for n_j in moduli[i + 1:]:
            if gcd(n_i, n_j) != 1:
                raise ValueError("Moduli must be pairwise coprime.")
    if any(not 0 <= c < n for c, n in zip(remainders, moduli)):
        raise ValueError("Each ciphertext must be in [0, modulus).")

    n_all = prod(moduli)
    total = 0
    for c_i, n_i in zip(remainders, moduli):
        partial = n_all // n_i
        inverse = pow(partial, -1, n_i)
        total += c_i * partial * inverse
    return total % n_all, n_all


def integer_nth_root(value: int, exponent: int) -> tuple[int, bool]:
    """Return (floor(value**(1/exponent)), exact) without floating point.

    Require value >= 0 and exponent >= 2. Binary search preserves the
    invariant low**exponent <= value < high**exponent.
    """
    _require_integer(value, "value")
    _require_integer(exponent, "exponent")
    if value < 0 or exponent < 2:
        raise ValueError("value must be >= 0 and exponent must be >= 2.")
    if value in (0, 1):
        return value, True
    low = 0
    high = 1 << ((value.bit_length() + exponent - 1) // exponent)
    while low + 1 < high:
        middle = (low + high) // 2
        if middle**exponent <= value:
            low = middle
        else:
            high = middle
    return low, low**exponent == value


def broadcast_attack(
    ciphertexts: Sequence[int], moduli: Sequence[int], exponent: int = 3
) -> AttackResult:
    """Combine public observations using CRT, then take an integer root.

    The caller must establish that ciphertexts use the same unpadded
    message and exponent. If M**exponent < product(moduli), CRT recovers
    M**exponent as an integer. This function cannot establish that bound
    without knowing M. Failure here does not prove Textbook RSA safe.
    """
    _require_integer(exponent, "exponent")
    if exponent < 2:
        raise ValueError("exponent must be >= 2.")
    combined, product = crt(ciphertexts, moduli)
    root, exact = integer_nth_root(combined, exponent)
    return AttackResult(combined, product, root, exact)


def message_to_integer(data: bytes) -> int:
    """Interpret nonempty bytes as an unsigned big-endian integer.

    Keep the original byte length separately to preserve leading zeros.
    This helper does not check the RSA-specific requirement M < n.
    """
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes.")
    if not data:
        raise ValueError("The message must not be empty.")
    return int.from_bytes(data, "big")


def integer_to_message(value: int, length: int) -> bytes:
    """Encode an unsigned integer into exactly length bytes, including zeros.

    Require a positive byte length and a value that fits. Invalid values
    raise ValueError rather than exposing an incidental OverflowError.
    """
    _require_integer(value, "value")
    _require_integer(length, "length")
    if value < 0 or length < 1:
        raise ValueError("value must be >= 0 and length must be >= 1.")
    if value.bit_length() > 8 * length:
        raise ValueError("value does not fit in the requested byte length.")
    return value.to_bytes(length, "big")
