# Screenshot Manifest — D2 / Problem 5

Five GAI evidence screenshots, ready for the report. Each entry gives the
figure caption, the prompt type to declare, and a draft "explanation of
output" line.

---

## gai_p5_01_build_prompt.png

**Caption:** Initial specification prompt and generated `tan_math.py`.

**Prompt type:** Role prompting, zero-shot.

**Explanation of output:** The prompt specified every constraint — no
`math` module, no factorials, period-π reduction, tolerance-based
termination, custom exceptions. The response supplied a complete module
plus a per-function rationale. I adopted the structure and the
incremental-term recurrence, and later renamed several functions for
clarity.

---

## gai_p5_02_compliance_check.png

**Caption:** Auditing the generated loops against the built-in
restriction.

**Prompt type:** Verification / constraint-checking.

**Explanation of output:** I challenged the loop construct against the
course rule permitting only input, output, arithmetic and interface
built-ins. The response confirmed compliance and enumerated every
built-in the module uses — `input`/`print` for I/O, `float`/`int` for
conversion, `abs` for arithmetic, `isinstance` for validation. I used
that enumeration as a compliance checklist against the specification.

---

## gai_p5_03_gui_prompt.png

**Caption:** Specification prompt for the Tkinter interface.

**Prompt type:** Role prompting, zero-shot.

**Explanation of output:** The prompt required the interface to contain
no mathematics of its own and to report errors as plain text rather than
tracebacks. The response supplied the widget layout and a rationale for
each control. NOTE: the version generated here called `compute_tan` with
two arguments, which is incompatible with the single-argument signature
in my module — see the note on integration testing below.

---

## gai_p5_04_defect_confirmation.png

**Caption:** Independent confirmation of the large-input precision
defect.

**Prompt type:** Verification, with source code supplied for review.

**Explanation of output:** The review confirmed the defect I had found in
testing: `tan(1e15)` returns −1.557 where the true value is −1.672, with
no error raised. It also correctly identified that the file I had pasted
was an earlier draft rather than my final version, which I then
corrected. The root cause is that the multiple of π selected during range
reduction becomes unreliable for very large arguments.

---

## gai_p5_05_final_review.png

**Caption:** Final compliance and accuracy review of the submitted
module.

**Prompt type:** Verification, with final source supplied.

**Explanation of output:** A full review of the submitted file. Compliance
confirmed — no `math` import, no factorial, no built-in trigonometry.
Exhaustive testing of every exact asymptote within ±1e6 raised
`UndefinedTangentError` in all cases with no misses, and boundary
behaviour was confirmed at ±1,000,000 accepted and ±1,000,001 rejected.
The review also observed that my documented accuracy figures were
conservative relative to measurement, which I noted in the module
comment.

---

# Still to capture

These require your own machine and cannot be supplied here.

## Interface states (4)

Run `python tan_gui.py`, then capture:

| Filename | Input | Expected |
|---|---|---|
| `gui_01_success.png` | `45`, degrees | 1.0000000000 |
| `gui_02_asymptote_error.png` | `90`, degrees | undefined-tangent message |
| `gui_03_invalid_input.png` | `abc` | not-a-number message |
| `gui_04_magnitude_guard.png` | `1e7`, radians | too-large message |

**Important:** any interface screenshot taken before the input limit was
tightened is now out of date. The message previously referred to a range
of ±1e10 and now refers to ±1,000,000. Retake all four.

## Tool output (3)

| Filename | Command |
|---|---|
| `terminal_no_ide.png` | `python tan_gui.py` run from a plain terminal |
| `flake8_clean.png` | `flake8 --max-line-length=79 tan_math.py tan_gui.py` |
| `pylint_score.png` | `pylint tan_math.py` (expect 10.00/10) |

## Repository (1)

| Filename | Content |
|---|---|
| `github_repo.png` | Repository page showing commit history and README |

---

# Final count

5 GAI + 4 interface + 3 tool output + 1 repository = **13 figures.**

That is the right density. Resist adding more numeric-result captures —
the verification table in the report covers those far better than a
sequence of near-identical windows.
