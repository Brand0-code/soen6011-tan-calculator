# Tangent Calculator — tan(x) from scratch

A desktop calculator for the tangent function, written in Python with a
Tkinter interface. The mathematics is implemented from first principles:
the `math` module is never imported, and no library routine performs any
part of the calculation.

**Course:** SOEN 6011 — Software Engineering Processes, Summer 2026
**Function:** F2 — tan(x)
**Version:** 1.1.0

---

## Running the program

Python 3.8 or newer is required. Tkinter ships with the standard CPython
installer on Windows and macOS; on Debian or Ubuntu it may need
`sudo apt install python3-tk`.

```bash
git clone https://github.com/Brand0-code/soen6011-tan-calculator.git
cd soen6011-tan-calculator/source_code
python tan_gui.py
```

No integrated development environment is needed, and there is no build
step. The calculation module can also be run on its own, which prints a
short self-check:

```bash
python tan_math.py
```

Both commands are run from `source_code/`. The three Python files must
stay together, since `tan_gui.py` imports from `tan_math.py`.

---

## Features

- Accepts an angle in either **radians** or **degrees**
- Results to ten decimal places
- Calculate button, and the **Return** key from anywhere in the window
- Clear button, and the **Escape** key
- Errors appear as plain sentences in the window, never as a traceback
- Every control carries a visible text label and is reachable by keyboard

---

## How it works

`tan(x)` is evaluated as `sin(x) / cos(x)`, with both terms taken from
their Maclaurin series.

| Step | Detail |
|---|---|
| Range reduction | The tangent repeats every π, so the nearest whole multiple of π is subtracted first. That places the argument in (−π/2, π/2], where the series converges quickly. |
| Series evaluation | Each term is obtained from the one before it by a single multiplication and division, so no factorial is ever computed and no intermediate value overflows. |
| Stopping rule | Summation ends once a term falls below 1e-15, rather than after a fixed number of terms. |
| Undefined points | If \|cos(x)\| falls below 1e-10 the angle sits on an asymptote, and `UndefinedTangentError` is raised. |

---

## Verification

The repository includes `verify_tan.py`, a harness that checks the module
against Python's own `math.tan`. It is not part of the implementation:
`math` is imported only there, never in `tan_math.py`.

```bash
cd source_code
python verify_tan.py
```

It runs 44 checks across reference angles, degree conversion, range
reduction, near-asymptote behaviour, undefined points, rejected input,
and the boundary of the accepted range. All 44 pass.

| Angle (radians) | This program | `math.tan` | Relative difference |
|---|---|---|---|
| π/4 | 1.0000000000 | 1.0000000000 | 1.1e-16 |
| 1.0 | 1.5574077247 | 1.5574077247 | 1.4e-16 |
| 2.0 | −2.1850398633 | −2.1850398633 | 2.0e-16 |
| 1000.0 | 1.4703241557 | 1.4703241557 | 3.8e-14 |
| 12345.678 | −0.9914971407 | −0.9914971407 | 1.5e-12 |
| 1.57 | 1255.7655915007 | 1255.7655915008 | 3.5e-14 |
| 89.999° | 57295.7795072025 | 57295.7795072129 | 1.8e-13 |
| 1e6 | −0.3736244539 | −0.3736244540 | 9.4e-11 |

---

## Code quality

Both modules and the verification harness conform to PEP 8 and are free
of static-analysis warnings.

```bash
cd source_code
flake8 --max-line-length=79 tan_math.py tan_gui.py verify_tan.py \
    test_tan_math.py pdb_demo.py check_contrast.py
pylint tan_math.py tan_gui.py verify_tan.py test_tan_math.py \
    pdb_demo.py check_contrast.py
```

| Check | Result |
|---|---|
| Flake8, 79-column limit, all six modules | no issues |
| Pylint, all six modules, single combined run | 10.00 / 10 |
| Unit tests | 58 of 58 passed |
| Verification harness | 44 of 44 checks passed |

Three suppressions are declared in the source, each with the reason
alongside it. `tan_math.py` disables `comparison-with-itself`, since
comparing a value to itself is the intended way to detect NaN without
calling `math.isnan`. `tan_gui.py` disables `too-many-ancestors`,
because `ttk.Frame` already inherits through six classes and any
subclass of it exceeds the default limit; the depth belongs to Tkinter
rather than to this code. `tan_math.py` also disables `duplicate-code`
around its self-check sample list, which coincidentally overlaps with
`verify_tan.py`'s list of reference angles; keeping the harness
independent of the module it checks matters more than removing the
short overlap.

---

## Accuracy and validated range

**Validated input range: −1e6 to 1e6.**

Range reduction subtracts a whole multiple of π, and the error in that
product grows with the size of the multiple. Sampling four thousand
angles at each order of magnitude and comparing against `math.tan` shows
roughly one significant digit lost per factor of ten:

| Input magnitude | Typical correct digits | Worst observed |
|---|---|---|
| 1e2 | 13.6 | 10.8 |
| 1e3 | 12.7 | 10.1 |
| 1e4 | 11.7 | 8.8 |
| 1e5 | 10.7 | 8.5 |
| 1e6 | 9.7 | 6.8 |
| 1e7 | 8.7 | 6.2 |
| 1e8 | 7.7 | 5.1 |
| 1e9 | 6.7 | 4.2 |

Results are shown to ten decimal places. At 1e6 the typical answer still
carries about ten correct digits and the worst case roughly seven, so the
display remains broadly honest. Past that the worst case falls below six
and the figures on screen would increasingly be noise presented as
precision, so 1e6 is where the limit is set. Angles beyond it are
rejected with an explanation rather than answered.

Testing at 1e15 showed the failure plainly: the program returned −1.557
where the true value is −1.672, with no outward sign of trouble. That
result prompted the limit. Production libraries avoid the problem with
Payne–Hanek reduction, which is beyond the scope of this deliverable.

Every exact asymptote within the accepted range — all 636,620 of them,
counting both signs — was tested and correctly raised
`UndefinedTangentError`, with no misses.

---

## Error handling

Two exception classes are defined, both inheriting from a shared
`TanCalculatorError` so that the interface can catch either with a single
handler.

| Situation | Response |
|---|---|
| Angle on an asymptote | `UndefinedTangentError` |
| Infinity, NaN, or a value beyond ±1e6 | `InvalidInputError` |
| Empty field or non-numeric text | Reported by the interface before any calculation |

Messages state what went wrong and what to do instead, rather than
reporting a fault code.

---

## Accessibility

No single colour can meet the WCAG 1.4.3 contrast ratio of 4.5:1
against both a light and a dark background — the required luminance
ranges do not overlap — so `tan_gui.py` reads the theme background at
run time and selects a palette to match. Measured ratios are
6.9–7.1:1 on light and 6.5–7.6:1 on dark, reproducible with
`source_code/check_contrast.py` rather than only asserted.

Every outcome is stated in words as well as colour, every control is
reachable from the keyboard (`Return` calculates, `Escape` clears),
and focus is visibly indicated. Screen-reader conformance is not
claimed: Tkinter exposes no accessibility tree on any platform, so
WCAG 4.1.2 and 4.1.3 cannot be met within this framework — that
limitation is documented rather than worked around.

---

## Repository layout

```
source_code/
  tan_math.py        calculation only, no interface code
  tan_gui.py         Tkinter interface, no calculation code
  verify_tan.py      verification harness, not part of the implementation
  test_tan_math.py   PyUnit suite (58 tests)
  pdb_demo.py        small driver used for the debugger walkthrough
  check_contrast.py  reproducible WCAG 1.4.3 check for the GUI palette
latex/
  main.tex          Deliverable 3 written report (Problem 7 and 8)
  poster.tex        Deliverable 3 A0 digital poster
  mindmap.tex       Deliverable 3 UI design principles mind map
pdf/
  main.pdf, poster.pdf, mindmap.pdf   compiled outputs
screenshots/      interface states and tool output
.gitignore
README.md
```

The calculation and interface modules are kept apart so that the
mathematics can be tested
without a window on screen.

---

## Versioning

Semantic Versioning (`MAJOR.MINOR.PATCH`). `v1.0.0` was the Deliverable 2
release. Deliverable 3 adds backward-compatible functionality only —
accessibility support in the GUI, a PyUnit suite, and a debugger demo —
so it is tagged **v1.1.0**, a minor version bump.

---

## Author

Student ID 40373534 — Concordia University, Department of Computer
Science and Software Engineering.
