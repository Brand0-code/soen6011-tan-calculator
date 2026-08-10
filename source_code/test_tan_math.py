"""Unit tests for the from-scratch tangent module.

SOEN 6011 -- Deliverable 3, Problem 8
Framework: PyUnit (the ``unittest`` module of the standard library).

Tests are organised by the behaviour under examination rather than by
function, so that each class corresponds to a requirement recorded in
Deliverable 2, Problem 7. The identifier is named in each docstring.

``math`` is imported here as an independent reference for the expected
values. It is confined to this file and is never imported by the
implementation; ``TestFromScratchConstraint`` asserts that mechanically.

Run every test:

    python -m unittest test_tan_math -v

Run one class:

    python -m unittest test_tan_math.TestUndefinedPoints -v
"""

import math
import unittest

from tan_math import (
    EPSILON,
    HALF_PI,
    MAX_MAGNITUDE,
    MAX_TERMS,
    PI,
    TOLERANCE,
    InvalidInputError,
    TanCalculatorError,
    UndefinedTangentError,
    compute_tan,
    cosine,
    degrees_to_radians,
    reduce_range,
    sine,
    validate_number,
)

PLACES = 9


class TestReferenceAngles(unittest.TestCase):
    """Known values of the tangent (TAN-FR-01, TAN-FR-03)."""

    def test_zero(self):
        """The tangent of zero is zero."""
        self.assertAlmostEqual(compute_tan(0.0), 0.0, places=PLACES)

    def test_pi_over_four(self):
        """The tangent of pi/4 is one."""
        self.assertAlmostEqual(compute_tan(PI / 4.0), 1.0, places=PLACES)

    def test_pi_over_six(self):
        """The tangent of pi/6 is one over the square root of three."""
        self.assertAlmostEqual(compute_tan(PI / 6.0),
                               1.0 / math.sqrt(3.0), places=PLACES)

    def test_pi_over_three(self):
        """The tangent of pi/3 is the square root of three."""
        self.assertAlmostEqual(compute_tan(PI / 3.0), math.sqrt(3.0),
                               places=PLACES)

    def test_odd_symmetry(self):
        """The tangent is odd, so tan(-x) equals -tan(x)."""
        for value in (0.5, 1.0, 1.2, 2.0):
            with self.subTest(x=value):
                self.assertAlmostEqual(compute_tan(-value),
                                       -compute_tan(value), places=PLACES)

    def test_integer_argument(self):
        """An integer argument is accepted and converted."""
        self.assertAlmostEqual(compute_tan(1), math.tan(1.0), places=PLACES)

    def test_matches_reference(self):
        """Results agree with an independent implementation."""
        for value in (0.1, 0.5, 1.0, -1.0, 2.0, -2.5, 3.0):
            with self.subTest(x=value):
                self.assertAlmostEqual(compute_tan(value), math.tan(value),
                                       places=PLACES)


class TestDegreeConversion(unittest.TestCase):
    """Angles supplied in degrees (TAN-FR-08, TAN-FR-09)."""

    def test_forty_five_degrees(self):
        """Forty-five degrees gives a tangent of one."""
        self.assertAlmostEqual(compute_tan(degrees_to_radians(45.0)), 1.0,
                               places=PLACES)

    def test_sixty_degrees(self):
        """Sixty degrees gives the square root of three."""
        self.assertAlmostEqual(compute_tan(degrees_to_radians(60.0)),
                               math.sqrt(3.0), places=PLACES)

    def test_half_turn(self):
        """A half turn returns to zero."""
        self.assertAlmostEqual(compute_tan(degrees_to_radians(180.0)), 0.0,
                               places=PLACES)

    def test_full_turn_plus_forty_five(self):
        """A full turn beyond forty-five degrees gives the same result."""
        self.assertAlmostEqual(compute_tan(degrees_to_radians(405.0)), 1.0,
                               places=PLACES)

    def test_conversion_factor(self):
        """One hundred and eighty degrees equals PI radians."""
        self.assertAlmostEqual(degrees_to_radians(180.0), PI, places=PLACES)

    def test_quarter_turn_conversion(self):
        """Ninety degrees equals half of PI."""
        self.assertAlmostEqual(degrees_to_radians(90.0), HALF_PI,
                               places=PLACES)


class TestRangeReduction(unittest.TestCase):
    """Periodicity and large arguments (TAN-FR-04)."""

    def test_reduction_preserves_the_tangent(self):
        """Reduction changes the argument but not the tangent.

        This is the invariant that matters. An earlier version of this
        class asserted only that the reduced angle was small, which a
        function returning a constant would also satisfy.
        """
        for value in (0.3, 1.0, 10.0, 100.0, 1000.0, -750.25, 12345.678):
            with self.subTest(x=value):
                self.assertAlmostEqual(math.tan(reduce_range(value)),
                                       math.tan(value), places=6)

    def test_reduced_angle_is_small(self):
        """Reduction confines the argument to within a quarter turn."""
        for value in (0.0, 1.0, 10.0, 100.0, 1000.0, -750.25):
            with self.subTest(x=value):
                self.assertLessEqual(abs(reduce_range(value)),
                                     HALF_PI + 1e-9)

    def test_reduction_is_identity_near_zero(self):
        """An argument already in range is returned unchanged."""
        for value in (0.0, 0.5, -0.5, 1.4, -1.4):
            with self.subTest(x=value):
                self.assertAlmostEqual(reduce_range(value), value,
                                       places=PLACES)

    def test_period_is_pi(self):
        """Adding a whole multiple of PI leaves the tangent unchanged."""
        base = 0.7
        for multiple in (1, 2, 5, 50):
            with self.subTest(k=multiple):
                self.assertAlmostEqual(compute_tan(base + multiple * PI),
                                       compute_tan(base), places=PLACES)

    def test_large_arguments(self):
        """Large angles still agree with the reference."""
        for value in (100.0, 1000.0, -500.5, 12345.678, 1e5):
            with self.subTest(x=value):
                self.assertAlmostEqual(compute_tan(value), math.tan(value),
                                       places=6)


class TestNearAsymptote(unittest.TestCase):
    """Behaviour close to, but not at, an undefined point."""

    def test_large_magnitude_near_asymptote(self):
        """The tangent grows without bound approaching pi/2."""
        self.assertGreater(compute_tan(1.5707), 1000.0)

    def test_accuracy_near_asymptote(self):
        """Results remain accurate close to the asymptote."""
        for value in (1.5, 1.57, 1.5707):
            with self.subTest(x=value):
                self.assertAlmostEqual(compute_tan(value) / math.tan(value),
                                       1.0, places=6)

    def test_eighty_nine_degrees(self):
        """An angle short of ninety degrees is computed, not refused."""
        self.assertAlmostEqual(compute_tan(degrees_to_radians(89.0)),
                               math.tan(math.radians(89.0)), places=6)


class TestUndefinedPoints(unittest.TestCase):
    """Angles where the tangent does not exist (TAN-FR-07)."""

    def test_half_pi(self):
        """A quarter turn is undefined."""
        with self.assertRaises(UndefinedTangentError):
            compute_tan(HALF_PI)

    def test_negative_half_pi(self):
        """A quarter turn in the negative direction is undefined."""
        with self.assertRaises(UndefinedTangentError):
            compute_tan(-HALF_PI)

    def test_odd_multiples(self):
        """Every odd multiple of pi/2 is undefined."""
        for multiple in (1, 3, 5, 7, 101, 1001):
            with self.subTest(k=multiple):
                with self.assertRaises(UndefinedTangentError):
                    compute_tan(multiple * HALF_PI)

    def test_ninety_degrees(self):
        """Odd multiples of ninety degrees are undefined."""
        for degrees in (90.0, -90.0, 270.0, 450.0):
            with self.subTest(degrees=degrees):
                with self.assertRaises(UndefinedTangentError):
                    compute_tan(degrees_to_radians(degrees))

    def test_even_multiples_are_defined(self):
        """Even multiples of pi/2 are ordinary zeros, not asymptotes."""
        for multiple in (0, 2, 4, 100):
            with self.subTest(k=multiple):
                self.assertAlmostEqual(compute_tan(multiple * HALF_PI), 0.0,
                                       places=6)

    def test_message_is_explanatory(self):
        """The message explains the cause rather than naming a fault."""
        with self.assertRaises(UndefinedTangentError) as caught:
            compute_tan(HALF_PI)
        message = str(caught.exception).lower()
        self.assertIn("undefined", message)
        self.assertIn("cosine", message)


class TestRejectedInput(unittest.TestCase):
    """Values that are not usable angles (TAN-FR-10, TAN-FR-12)."""

    def test_not_a_number(self):
        """NaN is rejected."""
        with self.assertRaises(InvalidInputError):
            compute_tan(float("nan"))

    def test_infinities(self):
        """Both infinities are rejected."""
        for value in (float("inf"), float("-inf")):
            with self.subTest(x=value):
                with self.assertRaises(InvalidInputError):
                    compute_tan(value)

    def test_non_numeric_types(self):
        """Values that are not numbers are rejected."""
        for value in ("abc", None, [], {}, (1, 2)):
            with self.subTest(value=value):
                with self.assertRaises(InvalidInputError):
                    compute_tan(value)

    def test_booleans(self):
        """Booleans are rejected despite being integers in Python."""
        for value in (True, False):
            with self.subTest(value=value):
                with self.assertRaises(InvalidInputError):
                    compute_tan(value)

    def test_message_suggests_an_action(self):
        """The message tells the user what to enter instead."""
        with self.assertRaises(InvalidInputError) as caught:
            compute_tan("abc")
        self.assertIn("number", str(caught.exception).lower())


class TestValidationGuards(unittest.TestCase):
    """Each guard in validate_number is reached and distinguishable.

    Testing only through compute_tan cannot show which guard rejected a
    value. Mutation analysis found that the infinity guard could be
    deleted without any test failing, because the magnitude guard caught
    the same input afterwards. These tests examine each guard directly.
    """

    def test_nan_reports_not_a_number(self):
        """NaN is refused for being NaN, not for its magnitude."""
        with self.assertRaises(InvalidInputError) as caught:
            validate_number(float("nan"))
        self.assertIn("not a number", str(caught.exception).lower())

    def test_infinity_reports_infinity(self):
        """Infinity is refused for being infinite, not for magnitude."""
        for value in (float("inf"), float("-inf")):
            with self.subTest(x=value):
                with self.assertRaises(InvalidInputError) as caught:
                    validate_number(value)
                self.assertIn("infinite", str(caught.exception).lower())

    def test_oversized_reports_the_range(self):
        """A finite oversized value is refused for its magnitude."""
        with self.assertRaises(InvalidInputError) as caught:
            validate_number(1e7)
        self.assertIn("large", str(caught.exception).lower())

    def test_valid_value_is_returned_as_float(self):
        """An acceptable value passes through as a float."""
        result = validate_number(42)
        self.assertIsInstance(result, float)
        self.assertEqual(result, 42.0)


class TestValidatedRange(unittest.TestCase):
    """The documented magnitude limit (TAN-FR-11)."""

    def test_limit_is_the_documented_value(self):
        """The constant matches the figure stated in the documentation.

        Asserting only relative to MAX_MAGNITUDE would let the constant
        drift while the error message continued to quote the old value.
        """
        self.assertEqual(MAX_MAGNITUDE, 1e6)

    def test_message_quotes_the_constant(self):
        """The message and the constant cannot drift apart."""
        with self.assertRaises(InvalidInputError) as caught:
            compute_tan(1e7)
        self.assertIn(str(int(MAX_MAGNITUDE)), str(caught.exception))

    def test_boundary_is_accepted(self):
        """An angle exactly at the limit is computed."""
        self.assertAlmostEqual(compute_tan(1e6), math.tan(1e6), places=6)

    def test_beyond_boundary_is_rejected(self):
        """An angle past the limit is refused."""
        for value in (1000001.0, 1e7, 1e15, -1e9):
            with self.subTest(x=value):
                with self.assertRaises(InvalidInputError):
                    compute_tan(value)


class TestTermination(unittest.TestCase):
    """Summation stops on tolerance, not on the iteration cap."""

    @staticmethod
    def _terms_used(x):
        """Count the terms the sine series consumes for this argument."""
        term = x
        count = 1
        k = 1
        while k < MAX_TERMS:
            term *= -x * x / ((2.0 * k) * (2.0 * k + 1.0))
            count += 1
            if abs(term) < TOLERANCE:
                break
            k += 1
        return count

    def test_terminates_well_before_the_cap(self):
        """The iteration cap is a safeguard, never the stopping rule."""
        for value in (0.01, 0.5, 1.0, HALF_PI):
            with self.subTest(x=value):
                self.assertLess(self._terms_used(value), 20)

    def test_smaller_arguments_need_fewer_terms(self):
        """Convergence is faster near zero, which is why reduction
        precedes summation."""
        self.assertLess(self._terms_used(0.01), self._terms_used(1.5))

    def test_cap_exceeds_observed_need(self):
        """The cap leaves ample margin over the worst observed case."""
        worst = max(self._terms_used(v) for v in (0.01, 0.5, 1.0, HALF_PI))
        self.assertGreater(MAX_TERMS, worst * 2)


class TestConstantsArePinned(unittest.TestCase):
    """The tuning constants are fixed to their documented values.

    Mutation analysis showed that TOLERANCE, EPSILON and MAX_TERMS
    could each be altered without any test failing, even where the
    change degraded accuracy by four orders of magnitude or caused a
    legitimate angle to be refused. These tests pin them.
    """

    def test_documented_values(self):
        """Each constant holds the value recorded in the module."""
        self.assertEqual(TOLERANCE, 1e-15)
        self.assertEqual(EPSILON, 1e-10)
        self.assertEqual(MAX_TERMS, 100)

    def test_angle_just_short_of_asymptote_is_computed(self):
        """A legitimate angle near the asymptote is not refused.

        This fails for any EPSILON wide enough to reject valid input.
        """
        self.assertGreater(compute_tan(HALF_PI - 1e-7), 1e6)

    def test_reduction_yields_non_negative_cosine(self):
        """Reduction guarantees the invariant the guard relies on.

        The asymptote test uses abs(cos_value). Removing the abs()
        passes every other test only because reduction happens to
        place the argument where cosine is non-negative. This asserts
        that dependency rather than leaving it implicit.
        """
        for value in (2.0, 3.0, 100.0, -50.0, 1000.0):
            with self.subTest(x=value):
                self.assertGreaterEqual(cosine(reduce_range(value)), 0.0)


class TestSubordinateFunctions(unittest.TestCase):
    """The series expansions used by the tangent (TAN-FR-05)."""

    def test_sine_known_values(self):
        """The sine series agrees with the reference."""
        for value in (0.0, 0.5, 1.0, -1.0, HALF_PI):
            with self.subTest(x=value):
                self.assertAlmostEqual(sine(value), math.sin(value),
                                       places=PLACES)

    def test_cosine_known_values(self):
        """The cosine series agrees with the reference."""
        for value in (0.0, 0.5, 1.0, -1.0, HALF_PI):
            with self.subTest(x=value):
                self.assertAlmostEqual(cosine(value), math.cos(value),
                                       places=PLACES)

    def test_pythagorean_identity(self):
        """The squares of the two series sum to one."""
        for value in (0.0, 0.3, 0.9, 1.4, -1.2):
            with self.subTest(x=value):
                total = sine(value) ** 2 + cosine(value) ** 2
                self.assertAlmostEqual(total, 1.0, places=PLACES)

    def test_sine_is_odd_and_cosine_is_even(self):
        """The series reproduce the symmetry of the functions."""
        for value in (0.4, 1.1, 1.5):
            with self.subTest(x=value):
                self.assertAlmostEqual(sine(-value), -sine(value),
                                       places=PLACES)
                self.assertAlmostEqual(cosine(-value), cosine(value),
                                       places=PLACES)

    def test_cosine_is_near_zero_at_the_asymptote(self):
        """The asymptote test rests on cosine vanishing there."""
        self.assertLess(abs(cosine(HALF_PI)), EPSILON)


class TestExceptionHierarchy(unittest.TestCase):
    """A single base class covers every failure (TAN-CON-02)."""

    def test_both_derive_from_the_base(self):
        """Each error can be caught through the common base class."""
        self.assertTrue(issubclass(UndefinedTangentError,
                                   TanCalculatorError))
        self.assertTrue(issubclass(InvalidInputError, TanCalculatorError))

    def test_base_catches_undefined(self):
        """An undefined point is caught by the base class."""
        with self.assertRaises(TanCalculatorError):
            compute_tan(HALF_PI)

    def test_base_catches_invalid(self):
        """Invalid input is caught by the base class."""
        with self.assertRaises(TanCalculatorError):
            compute_tan(float("nan"))

    def test_the_two_errors_are_distinct(self):
        """Neither error class is a subclass of the other."""
        self.assertFalse(issubclass(UndefinedTangentError,
                                    InvalidInputError))
        self.assertFalse(issubclass(InvalidInputError,
                                    UndefinedTangentError))


class TestFromScratchConstraint(unittest.TestCase):
    """No library performs the mathematics (TAN-FR-02)."""

    def test_module_does_not_import_math(self):
        """The implementation source contains no import of math."""
        # pylint: disable=import-outside-toplevel
        # Imported here rather than at the top because this test needs
        # the module object only to locate its source file.
        import tan_math
        with open(tan_math.__file__, encoding="utf-8") as source:
            lines = source.read().splitlines()
        offenders = [line for line in lines
                     if line.strip().startswith(("import math",
                                                 "from math"))]
        self.assertEqual(offenders, [])

    def test_module_does_not_use_factorial(self):
        """No factorial is computed anywhere in the implementation."""
        # pylint: disable=import-outside-toplevel
        import tan_math
        with open(tan_math.__file__, encoding="utf-8") as source:
            code = [line for line in source.read().splitlines()
                    if not line.strip().startswith("#")]
        self.assertNotIn("factorial(", "\n".join(code))

    def test_pi_is_declared_locally(self):
        """The module defines its own value for PI."""
        self.assertAlmostEqual(PI, math.pi, places=15)


if __name__ == "__main__":
    unittest.main(verbosity=2)
