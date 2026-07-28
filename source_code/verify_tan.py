"""Verification harness for tan_math.py.

SOEN 6011 -- Deliverable 2, Problem 5

This script is NOT part of the implementation. It exists only to check
the from-scratch module against Python's own ``math.tan`` as a reference.
The ``math`` import below is confined to this file; ``tan_math.py``
itself never imports it.

Run with:  python verify_tan.py
"""

import math

from tan_math import (
    MAX_MAGNITUDE,
    PI,
    InvalidInputError,
    UndefinedTangentError,
    compute_tan,
    degrees_to_radians,
)

PASS = "pass"
FAIL = "FAIL"


def check_value(label, radians, reference):
    """Compare compute_tan against a reference value."""
    try:
        mine = compute_tan(radians)
    except (UndefinedTangentError, InvalidInputError) as error:
        print(f"  {FAIL}  {label:<22} raised {type(error).__name__}")
        return False

    difference = abs(mine - reference)
    scale = abs(reference) if abs(reference) > 1.0 else 1.0
    relative = difference / scale
    verdict = PASS if relative < 1e-8 else FAIL
    print(
        f"  {verdict}  {label:<22} {mine:>22.10f}"
        f"  ref {reference:>22.10f}  rel {relative:.1e}"
    )
    return verdict == PASS


def check_raises(label, value, expected):
    """Confirm that a value raises the expected exception."""
    try:
        compute_tan(value)
    except expected:
        print(f"  {PASS}  {label:<22} raised {expected.__name__}")
        return True
    except Exception as error:  # pylint: disable=broad-except
        print(f"  {FAIL}  {label:<22} raised {type(error).__name__}")
        return False
    print(f"  {FAIL}  {label:<22} raised nothing")
    return False


def main():
    """Run every check and report a summary."""
    results = []

    print("\n1. REFERENCE ANGLES (radians)")
    for label, value in (
        ("0", 0.0),
        ("pi/6", PI / 6.0),
        ("pi/4", PI / 4.0),
        ("pi/3", PI / 3.0),
        ("1.0", 1.0),
        ("-1.0", -1.0),
        ("2.0", 2.0),
        ("-2.5", -2.5),
    ):
        results.append(check_value(label, value, math.tan(value)))

    print("\n2. DEGREES")
    for label, degrees in (
        ("0 deg", 0.0),
        ("30 deg", 30.0),
        ("45 deg", 45.0),
        ("60 deg", 60.0),
        ("-45 deg", -45.0),
        ("180 deg", 180.0),
        ("360 deg", 360.0),
        ("405 deg", 405.0),
    ):
        radians = degrees_to_radians(degrees)
        reference = math.tan(math.radians(degrees))
        results.append(check_value(label, radians, reference))

    print("\n3. PERIODICITY AND RANGE REDUCTION")
    for label, value in (
        ("10 pi + 0.3", 10.0 * PI + 0.3),
        ("100.0", 100.0),
        ("1000.0", 1000.0),
        ("-500.5", -500.5),
        ("12345.678", 12345.678),
        ("1e5", 1e5),
        ("1e6 (limit)", 1e6),
    ):
        results.append(check_value(label, value, math.tan(value)))

    print("\n4. NEAR THE ASYMPTOTE")
    for label, value in (
        ("1.5", 1.5),
        ("1.57", 1.57),
        ("1.5707", 1.5707),
        ("89 deg", degrees_to_radians(89.0)),
        ("89.999 deg", degrees_to_radians(89.999)),
    ):
        results.append(check_value(label, value, math.tan(value)))

    print("\n5. UNDEFINED POINTS")
    for label, value in (
        ("pi/2", PI / 2.0),
        ("-pi/2", -PI / 2.0),
        ("3pi/2", 3.0 * PI / 2.0),
        ("90 deg", degrees_to_radians(90.0)),
        ("270 deg", degrees_to_radians(270.0)),
        ("-90 deg", degrees_to_radians(-90.0)),
    ):
        results.append(check_raises(label, value, UndefinedTangentError))

    print("\n6. REJECTED INPUT")
    for label, value in (
        ("not a number", float("nan")),
        ("infinity", float("inf")),
        ("-infinity", float("-inf")),
        ("text", "abc"),
        ("None", None),
        ("True", True),
        ("1e7 (too large)", 1e7),
        ("limit + 1", MAX_MAGNITUDE + 1.0),
    ):
        results.append(check_raises(label, value, InvalidInputError))

    print("\n7. BOUNDARY OF THE ACCEPTED RANGE")
    results.append(check_value("1e6 accepted", 1e6, math.tan(1e6)))
    results.append(
        check_raises("1000001 rejected", 1000001.0, InvalidInputError)
    )

    passed = sum(1 for r in results if r)
    total = len(results)
    print("\n" + "=" * 60)
    print(f"  {passed} of {total} checks passed")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
