# Simply Supported Beam Calculator

A Python desktop calculator for simply supported beams with one or more partial uniform distributed loads. It displays support reactions and the maximum positive bending moment, with a beam schematic and shear and moment diagrams.

## Requirements

- Python 3
- Tkinter
- NumPy
- Matplotlib

Install the plotting and numerical dependencies if needed:

```sh
python3 -m pip install numpy matplotlib
```

Tkinter is included with many Python installers. On macOS, use a Python installation that includes Tk support.

## Run

From the project directory:

```sh
python3 app.py
```

The initial beam matches the validation example in `spec.md/spec.md`. Use the File menu to save or open beam inputs as JSON.

## Scope

The current calculation model supports a simply supported beam with one or more downward partial uniform loads. It does not calculate deflection, strength, or code compliance. See `spec.md/spec.md` for assumptions, equations, and validation values.
