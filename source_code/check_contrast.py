"""Reproducible WCAG 1.4.3 contrast check for the GUI's theme colours.

This exists so the contrast figures quoted in tan_gui.py and in the
poster are not just asserted: anyone can run this file and get the
same numbers back. It imports the colour constants directly from
tan_gui.py rather than duplicating the hex values, so the two cannot
drift apart the way the code comment and the poster text once did.

Usage:
    python check_contrast.py
        Auto-detects the live ttk theme background (light or dark,
        whichever the system is currently in) and reports the ratio
        for that theme's palette against it.

    python check_contrast.py --light-bg RRGGBB --dark-bg RRGGBB
        Reports both themes against explicitly supplied backgrounds,
        useful when the two ttk backgrounds cannot be read in the
        same run (macOS reports whichever appearance is currently
        active, not both at once).
"""
import argparse
import sys
import tkinter as tk
from tkinter import ttk

from tan_gui import DARK_THEME_COLOURS, DARK_THEME_THRESHOLD, \
    LIGHT_THEME_COLOURS

WCAG_AA_NORMAL_TEXT = 4.5


def relative_luminance(hex_colour: str) -> float:
    """Return the WCAG relative luminance of a ``#RRGGBB`` colour."""
    hex_colour = hex_colour.lstrip("#")
    channels = []
    for i in (0, 2, 4):
        value = int(hex_colour[i:i + 2], 16) / 255.0
        if value <= 0.03928:
            channels.append(value / 12.92)
        else:
            channels.append(((value + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] \
        + 0.0722 * channels[2]


def contrast_ratio(hex_a: str, hex_b: str) -> float:
    """Return the WCAG contrast ratio between two ``#RRGGBB`` colours."""
    lum_a, lum_b = relative_luminance(hex_a), relative_luminance(hex_b)
    lighter, darker = max(lum_a, lum_b), min(lum_a, lum_b)
    return (lighter + 0.05) / (darker + 0.05)


def report(theme_name: str, palette: dict, background: str) -> None:
    """Print the ratio for every colour in ``palette`` against a bg."""
    print(f"{theme_name} theme, background {background}:")
    for role, colour in palette.items():
        ratio = contrast_ratio(colour, background)
        verdict = "PASS" if ratio >= WCAG_AA_NORMAL_TEXT else "FAIL"
        print(f"  {role:8s} {colour}  {ratio:5.2f}:1  {verdict}")


def detect_live_background() -> str:
    """Return the current ttk TFrame background as ``#RRGGBB``."""
    root = tk.Tk()
    root.withdraw()
    name = ttk.Style().lookup("TFrame", "background")
    red, green, blue = (channel // 256 for channel in root.winfo_rgb(name))
    root.destroy()
    return f"#{red:02x}{green:02x}{blue:02x}"


def main() -> None:
    """Parse arguments and report contrast for the requested source."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--light-bg", metavar="RRGGBB")
    parser.add_argument("--dark-bg", metavar="RRGGBB")
    args = parser.parse_args()

    if args.light_bg or args.dark_bg:
        if args.light_bg:
            report("Light", LIGHT_THEME_COLOURS, "#" + args.light_bg)
        if args.dark_bg:
            report("Dark", DARK_THEME_COLOURS, "#" + args.dark_bg)
        return

    try:
        background = detect_live_background()
    # A live Tk display is inherently environment-dependent: it may be
    # absent (headless CI), or Tk/Tcl may fail in ways only its own
    # TclError names. Catching broadly here is the deliberate fallback
    # to the documented --light-bg/--dark-bg path, not an omission.
    except Exception as exc:  # pylint: disable=broad-exception-caught
        print(f"Could not read a live ttk background: {exc}")
        print("Pass --light-bg / --dark-bg explicitly instead.")
        sys.exit(1)

    luminance = relative_luminance(background)
    if luminance < DARK_THEME_THRESHOLD:
        report("Dark (detected live)", DARK_THEME_COLOURS, background)
    else:
        report("Light (detected live)", LIGHT_THEME_COLOURS, background)


if __name__ == "__main__":
    main()
