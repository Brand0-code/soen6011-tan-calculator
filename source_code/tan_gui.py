"""Graphical user interface for the from-scratch tangent calculator.

This module supplies the presentation layer of the SOEN 6011 calculator
for function F2. All mathematics lives in :mod:`tan_math`; nothing here
computes a tangent, which keeps the numerical core independently
testable and confines Tkinter to a single file.

The window offers a single entry field, a choice between degrees and
radians, and a result area that reports either an answer or a plain
explanation of what went wrong. Every control carries a text label and
is reachable from the keyboard, and the Return key activates the
calculation from anywhere in the window.

Launch the interface from a terminal, with no development environment
required::

    $ python tan_gui.py
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from tan_math import (
    TanCalculatorError,
    __version__,
    compute_tan,
    degrees_to_radians,
)

WINDOW_TITLE = "Tangent Calculator"
WINDOW_PADDING = 16
FIELD_WIDTH = 26
RESULT_DECIMALS = 10

RADIANS = "radians"
DEGREES = "degrees"

SUCCESS_COLOUR = "#0b6623"
ERROR_COLOUR = "#b00020"

PROMPT_TEXT = "Enter an angle and choose its unit, then select Calculate."
EMPTY_INPUT_MESSAGE = "Please enter an angle before calculating."
NON_NUMERIC_MESSAGE = (
    "That entry is not a number. Please enter a value such as 45 or 0.7854."
)


class TangentCalculatorApp(ttk.Frame):
    """The main application window.

    The frame owns every widget, holds the two variables bound to the
    entry field and the unit selector, and routes a calculation request
    to :func:`tan_math.compute_tan`.

    Attributes:
        angle_var: Text currently held by the entry field.
        unit_var: Either :data:`RADIANS` or :data:`DEGREES`.
        result_var: Text currently shown in the result area.
    """

    def __init__(self, master: tk.Misc) -> None:
        """Build the interface inside ``master``.

        Args:
            master: The parent widget, normally the root window.
        """
        super().__init__(master, padding=WINDOW_PADDING)

        self.angle_var = tk.StringVar()
        self.unit_var = tk.StringVar(value=RADIANS)
        self.result_var = tk.StringVar(value=PROMPT_TEXT)

        self._entry: ttk.Entry
        self._result_label: ttk.Label

        self._build_widgets()
        self._bind_keys()

    def _build_widgets(self) -> None:
        """Create and lay out every widget in the window."""
        self.grid(column=0, row=0, sticky="nsew")
        self.columnconfigure(0, weight=1)

        heading = ttk.Label(
            self,
            text="Tangent Calculator",
            font=("TkDefaultFont", 15, "bold"),
        )
        heading.grid(column=0, row=0, sticky="w")

        subheading = ttk.Label(
            self,
            text="Computes tan(x) without using Python's math library.",
            wraplength=340,
        )
        subheading.grid(column=0, row=1, sticky="w", pady=(2, 12))

        entry_label = ttk.Label(self, text="Angle:")
        entry_label.grid(column=0, row=2, sticky="w")

        self._entry = ttk.Entry(
            self,
            textvariable=self.angle_var,
            width=FIELD_WIDTH,
            font=("TkDefaultFont", 12),
        )
        self._entry.grid(column=0, row=3, sticky="ew", pady=(2, 12))

        units = ttk.LabelFrame(self, text="Unit", padding=8)
        units.grid(column=0, row=4, sticky="ew")

        radians_button = ttk.Radiobutton(
            units,
            text="Radians",
            value=RADIANS,
            variable=self.unit_var,
        )
        radians_button.grid(column=0, row=0, sticky="w", padx=(0, 16))

        degrees_button = ttk.Radiobutton(
            units,
            text="Degrees",
            value=DEGREES,
            variable=self.unit_var,
        )
        degrees_button.grid(column=1, row=0, sticky="w")

        buttons = ttk.Frame(self)
        buttons.grid(column=0, row=5, sticky="ew", pady=12)
        buttons.columnconfigure(0, weight=1)
        buttons.columnconfigure(1, weight=1)

        calculate_button = ttk.Button(
            buttons,
            text="Calculate",
            command=self.calculate,
        )
        calculate_button.grid(column=0, row=0, sticky="ew", padx=(0, 6))

        clear_button = ttk.Button(
            buttons,
            text="Clear",
            command=self.clear,
        )
        clear_button.grid(column=1, row=0, sticky="ew", padx=(6, 0))

        result_frame = ttk.LabelFrame(self, text="Result", padding=10)
        result_frame.grid(column=0, row=6, sticky="ew")
        result_frame.columnconfigure(0, weight=1)

        self._result_label = ttk.Label(
            result_frame,
            textvariable=self.result_var,
            wraplength=340,
            justify="left",
        )
        self._result_label.grid(column=0, row=0, sticky="w")

        footer = ttk.Label(
            self,
            text=f"SOEN 6011 - F2 tan(x) - version {__version__}",
        )
        footer.grid(column=0, row=7, sticky="w", pady=(12, 0))

        self._entry.focus_set()

    def _bind_keys(self) -> None:
        """Bind the keyboard shortcuts offered by the window."""
        self.winfo_toplevel().bind("<Return>", self._on_return)
        self.winfo_toplevel().bind("<KP_Enter>", self._on_return)
        self.winfo_toplevel().bind("<Escape>", self._on_escape)

    def _on_return(self, _event: tk.Event) -> None:
        """Handle the Return key by calculating.

        Args:
            _event: The Tkinter event, which is not needed here.
        """
        self.calculate()

    def _on_escape(self, _event: tk.Event) -> None:
        """Handle the Escape key by clearing the form.

        Args:
            _event: The Tkinter event, which is not needed here.
        """
        self.clear()

    def _show(self, message: str, *, is_error: bool) -> None:
        """Display a message in the result area.

        Colour marks the outcome, and the wording states it as well, so
        the interface remains usable without colour perception.

        Args:
            message: The text to display.
            is_error: Whether the message reports a failure.
        """
        self.result_var.set(message)
        self._result_label.configure(
            foreground=ERROR_COLOUR if is_error else SUCCESS_COLOUR
        )

    def calculate(self) -> None:
        """Read the form, compute the tangent and report the outcome.

        Input that is empty or non-numeric is reported directly. Any
        failure raised by the calculation layer is caught through its
        common base class and shown in the wording supplied there.
        """
        raw_text = self.angle_var.get().strip()

        if not raw_text:
            self._show(EMPTY_INPUT_MESSAGE, is_error=True)
            return

        try:
            angle = float(raw_text)
        except ValueError:
            self._show(NON_NUMERIC_MESSAGE, is_error=True)
            return

        in_degrees = self.unit_var.get() == DEGREES

        try:
            radians = degrees_to_radians(angle) if in_degrees else angle
            result = compute_tan(radians)
        except TanCalculatorError as error:
            self._show(f"Cannot calculate: {error}", is_error=True)
            return

        unit_name = DEGREES if in_degrees else RADIANS
        self._show(
            f"tan({raw_text} {unit_name}) = {result:.{RESULT_DECIMALS}f}",
            is_error=False,
        )

    def clear(self) -> None:
        """Empty the entry field and restore the opening prompt."""
        self.angle_var.set("")
        self._show(PROMPT_TEXT, is_error=False)
        self._entry.focus_set()


def main() -> None:
    """Create the root window and start the event loop."""
    root = tk.Tk()
    root.title(WINDOW_TITLE)
    root.minsize(400, 440)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    TangentCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
