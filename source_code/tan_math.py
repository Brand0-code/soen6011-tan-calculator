"""From-scratch computation of the tangent function.

This module implements ``tan(x)`` without relying on Python's ``math``
module or on any other library routine for the mathematics. It is the
computational core of the SOEN 6011 calculator for function F2, and is
kept free of user-interface code so that it can be tested in isolation.

The implementation rests on the identity ``tan(x) = sin(x) / cos(x)``.
Both ``sin`` and ``cos`` are evaluated from their Maclaurin series, and
the argument is first reduced modulo :data:`PI` so that the series is
always evaluated close to zero, where it converges quickly.

Typical use::

    >>> from tan_math import compute_tan, degrees_to_radians
    >>> compute_tan(degrees_to_radians(45.0))
    1.0

Running the module directly executes a short self-check::

    $ python tan_math.py
"""

from __future__ import annotations

from typing import Union

__version__ = "1.1.0"
__all__ = [
    "PI",
    "HALF_PI",
    "MAX_MAGNITUDE",
    "TanCalculatorError",
    "UndefinedTangentError",
    "InvalidInputError",
    "validate_number",
    "degrees_to_radians",
    "reduce_range",
    "sine",
    "cosine",
    "compute_tan",
]

#: Ratio of a circle's circumference to its diameter, to double precision.
#: Declared as a literal so that ``math.pi`` is not required.
PI = 3.14159265358979323846

#: A quarter turn in radians; the first positive asymptote of the tangent.
HALF_PI = PI / 2.0

#: A series term below this magnitude no longer changes the running total
#: at double precision, so summation stops rather than running a fixed
#: number of iterations.
TOLERANCE = 1e-15

#: A cosine whose magnitude falls below this is treated as zero, meaning
#: the angle sits on an asymptote and the tangent is undefined.
EPSILON = 1e-10

#: Largest magnitude accepted for an angle in radians.
#:
#: Range reduction subtracts ``k * PI``, and the error in that product
#: grows with ``k``. Sampling four thousand angles at each order of
#: magnitude against ``math.tan`` shows about one significant digit lost
#: per factor of ten:
#:
#: ===============  ==============  ==============
#: Input magnitude  Typical digits  Worst observed
#: ===============  ==============  ==============
#: 1e2              13.6            10.8
#: 1e3              12.7            10.1
#: 1e4              11.7             8.8
#: 1e5              10.7             8.5
#: 1e6               9.7             6.8
#: 1e7               8.7             6.2
#: 1e8               7.7             5.1
#: ===============  ==============  ==============
#:
#: Results are reported to ten decimal places. At 1e6 the worst case
#: still holds about seven correct digits; past that it falls below six
#: and the display would increasingly show noise as precision. Every
#: exact asymptote within this range was also tested and correctly
#: detected as undefined.
MAX_MAGNITUDE = 1e6

#: Upper bound on series iterations, guarding against a non-terminating
#: loop should an unexpected value ever reach the expansions.
MAX_TERMS = 100

#: Values accepted by the public functions before validation.
Number = Union[int, float]


class TanCalculatorError(Exception):
    """Base class for every error raised by the calculator.

    Catching this single class is sufficient for a caller that wants to
    treat all calculator failures uniformly, such as the graphical user
    interface in :mod:`tan_gui`.
    """


class UndefinedTangentError(TanCalculatorError):
    """Raised when the tangent of the requested angle does not exist.

    The tangent is undefined at every odd multiple of ``pi / 2``, where
    the cosine equals zero and the function grows without bound.
    """


class InvalidInputError(TanCalculatorError):
    """Raised when the supplied value is not a finite real number.

    Non-numeric values, infinities and NaN are all rejected, since none
    of them denotes an angle for which a tangent can be computed.
    """


def validate_number(value: object) -> float:
    """Return ``value`` as a finite float.

    Two properties of IEEE-754 arithmetic remove any need for
    ``math.isnan`` or ``math.isinf``: NaN is the only value that differs
    from itself, and each infinity compares equal to the corresponding
    literal.

    Args:
        value: The value to validate. Booleans are rejected even though
            Python treats them as integers, because ``True`` is not a
            meaningful angle.

    Returns:
        The value converted to a finite ``float``.

    Raises:
        InvalidInputError: If the value is non-numeric, infinite, NaN,
            or larger in magnitude than :data:`MAX_MAGNITUDE`.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InvalidInputError(
            "Please enter a number, for example 45 or 0.7854."
        )

    number = float(value)

    # pylint: disable=comparison-with-itself
    # The comparison is deliberate: NaN is the only value unequal to
    # itself, which detects it without calling math.isnan.
    if number != number:
        raise InvalidInputError(
            "That value is not a number, so its tangent cannot be found."
        )

    if number in (float("inf"), float("-inf")):
        raise InvalidInputError(
            "That value is infinite. Please enter a finite angle."
        )

    if abs(number) > MAX_MAGNITUDE:
        raise InvalidInputError(
            "That angle is too large to give a trustworthy answer. Please "
            "enter a value between -1000000 and 1000000. Beyond that range "
            "the angle cannot be reduced precisely enough for the result to "
            "be accurate to the number of decimal places shown."
        )

    return number


def degrees_to_radians(degrees: Number) -> float:
    """Convert an angle from degrees to radians.

    A half turn spans 180 degrees or :data:`PI` radians, which gives the
    conversion factor used here.

    Args:
        degrees: The angle expressed in degrees.

    Returns:
        The same angle expressed in radians.

    Raises:
        InvalidInputError: If the angle is not a finite number.
    """
    return validate_number(degrees) * PI / 180.0


def _nearest_integer(value: float) -> float:
    """Round ``value`` to the nearest whole number.

    ``int`` truncates towards zero, so half a unit is added to positive
    values and subtracted from negative ones before truncating.

    Args:
        value: The number to round.

    Returns:
        The nearest whole number, as a float.
    """
    if value >= 0.0:
        return float(int(value + 0.5))
    return float(int(value - 0.5))


def reduce_range(x: float) -> float:
    """Reduce an angle to the equivalent angle nearest zero.

    The tangent repeats every :data:`PI` radians, so subtracting the
    nearest whole multiple of :data:`PI` leaves the result unchanged
    while confining the argument to ``(-pi/2, pi/2]``. This matters for
    accuracy: the Maclaurin series converges rapidly near zero and
    poorly for an argument such as ``x = 1000``.

    Args:
        x: The angle in radians.

    Returns:
        The reduced angle, in ``(-pi/2, pi/2]``.
    """
    return x - _nearest_integer(x / PI) * PI


def sine(x: float) -> float:
    """Compute the sine of an angle from its Maclaurin series.

    The expansion is ``x - x**3/3! + x**5/5! - ...``. Rather than
    evaluating powers and factorials directly, each term is derived from
    its predecessor by multiplying by ``-x**2 / ((2k)(2k + 1))``. That
    recurrence avoids factorials entirely, costs one multiplication and
    one division per term, and cannot overflow.

    Args:
        x: The angle in radians, expected to be range-reduced.

    Returns:
        The sine of the angle.
    """
    term = x
    total = x
    k = 1
    while k < MAX_TERMS:
        term *= -x * x / ((2.0 * k) * (2.0 * k + 1.0))
        total += term
        if abs(term) < TOLERANCE:
            break
        k += 1
    return total


def cosine(x: float) -> float:
    """Compute the cosine of an angle from its Maclaurin series.

    The expansion is ``1 - x**2/2! + x**4/4! - ...``, evaluated with the
    same recurrence used in :func:`sine`, here multiplying each term by
    ``-x**2 / ((2k - 1)(2k))``.

    Args:
        x: The angle in radians, expected to be range-reduced.

    Returns:
        The cosine of the angle.
    """
    term = 1.0
    total = 1.0
    k = 1
    while k < MAX_TERMS:
        term *= -x * x / ((2.0 * k - 1.0) * (2.0 * k))
        total += term
        if abs(term) < TOLERANCE:
            break
        k += 1
    return total


def compute_tan(x_radians: Number) -> float:
    """Compute the tangent of an angle given in radians.

    Args:
        x_radians: The angle in radians.

    Returns:
        The tangent of the angle.

    Raises:
        InvalidInputError: If the angle is not a finite number.
        UndefinedTangentError: If the angle lies on an asymptote, that
            is at an odd multiple of ``pi / 2``.

    Examples:
        >>> compute_tan(0.0)
        0.0
        >>> compute_tan(PI / 4.0)
        1.0
    """
    reduced = reduce_range(validate_number(x_radians))
    cos_value = cosine(reduced)

    if abs(cos_value) < EPSILON:
        raise UndefinedTangentError(
            "The tangent is undefined at this angle. Angles that are odd "
            "multiples of 90 degrees, or pi/2 radians, have a cosine of "
            "zero, and there the tangent grows without bound."
        )

    return sine(reduced) / cos_value


def _self_check() -> None:
    """Print the tangent of several angles, including the error cases."""
    print(f"tan(x) from-scratch module, version {__version__}")
    print("-" * 60)

    # pylint: disable=duplicate-code
    # This sample list intentionally overlaps with verify_tan.py's list
    # of reference angles: both exist to exercise the same well-known
    # values, one as a quick manual demo and the other as an automated
    # check against math.tan. Sharing the source list would make the
    # verification harness depend on the module it is meant to check
    # independently, so the short overlap is kept rather than removed.
    samples = (
        ("0", 0.0),
        ("pi/6", PI / 6.0),
        ("pi/4", PI / 4.0),
        ("pi/3", PI / 3.0),
        ("1.0", 1.0),
        ("-1.0", -1.0),
        ("1000.0", 1000.0),
        ("45 degrees", degrees_to_radians(45.0)),
    )
    for label, angle in samples:
        print(f"  tan({label:<12}) = {compute_tan(angle):.10f}")

    print("-" * 60)
    for label, value in (("pi/2", HALF_PI), ("not a number", float("nan"))):
        try:
            compute_tan(value)
        except TanCalculatorError as error:
            print(f"  tan({label}) -> {error}")


if __name__ == "__main__":
    _self_check()
