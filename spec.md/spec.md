# Simply Supported Beam Calculator

## Purpose

A Python desktop application for analyzing a simply supported beam under a uniform distributed load. It reports support reactions and the maximum bending moment, and plots the beam's shear and moment diagrams. The first version supports one uniform load over a user-selected portion of the beam.

## Platform

- Python desktop app using Tkinter, started with `python app.py`.
- Keep calculations in their own module, separate from the window code.
- Use NumPy for numerical calculations and Matplotlib for diagrams embedded in the Tkinter window.

## Model and assumptions

- The beam is straight, prismatic, and simply supported at (x=0) and (x=L).
- The beam span (L) is measured in feet.
- The beam section is identified by a text label such as `W18x35`. The label is informational; section strength, deflection, and self-weight calculations are outside this calculator's scope.
- One downward uniform distributed load of intensity (w) acts from position (a) to position (b), where (0 \le a < b \le L).
- Use kip for force, kip/ft for distributed load, and kip-ft for moment.
- Use static equilibrium with the usual sign convention: positive support reactions act upward, positive shear is upward on the left face, and positive sagging moment is plotted above the axis.

## Inputs

| Input | Units | Meaning |
|---|---|---|
| Beam span, (L) | ft | Distance between supports |
| Beam section | — | Descriptive label, for example `W18x35` |
| Uniform load, (w) | kip/ft | Downward load intensity |
| Load start, (a) | ft | Position where the distributed load begins, measured from the left support |
| Load end, (b) | ft | Position where the distributed load ends, measured from the left support |

Provide editable numeric controls with units shown beside their labels. The section label is free text. Numeric inputs must be finite; require (L>0), (w\ge0), and (0\le a<b\le L). Reject invalid or empty input, explain the constraint, and do not display results calculated from invalid values.

## Calculations

Let (Q=w(b-a)) be the resultant of the distributed load, acting at its centroid (x_c=(a+b)/2).

Calculate the reactions from equilibrium:

\[
R_B=\frac{Qx_c}{L}, \qquad R_A=Q-R_B
\]

For positions (0\le x\le L), calculate shear and bending moment using the load intensity active between (a) and (b):

\[
V(x)=R_A-w\max\left(0,\min(x,b)-a\right)
\]

\[
M(x)=R_Ax-\frac{w}{2}\max(0,x-a)^2+\frac{w}{2}\max(0,x-b)^2
\]

The formulas must also work when the load starts after the left support or ends before the right support. Find the maximum positive bending moment over the span and report its location. For a nonzero uniform load, include the zero-shear location inside the loaded interval when finding the maximum; also inspect interval boundaries and support locations. For zero load, report zero maximum moment at the supports.

Do not round values used in calculations. Round only for display: reactions and load intensity to a sensible number of decimals, and maximum moment and its location to one decimal place by default.

## Outputs

- Left and right support reactions, (R_A) and (R_B), in kips.
- Maximum positive bending moment in kip-ft and its position in feet from the left support.
- A beam schematic showing the supports, span, section label, and distributed load extent and direction.
- A shear-force diagram (V(x)) and bending-moment diagram (M(x)), with labeled axes and units. Mark the maximum moment and its location on the moment diagram.
- Update all results and diagrams whenever a valid input changes.

## Look and feel

Use a clean, professional layout in a resizable desktop window. Place input controls in a panel on the left and the beam schematic, key results, and diagrams on the right. Keep reactions and maximum moment easy to find, with readable labels, sufficient spacing, and clear contrast. Calculate and display the default values when the window opens.

## Validation

Use this case to verify the calculations:

- Support condition: simply supported
- Beam span: (L=30\ \text{ft})
- Section label: `W18x35`
- Uniform distributed load: (w=2\ \text{kips/ft}), downward, from (a=0\ \text{ft}) to (b=15\ \text{ft})

The resultant load is (Q=2(15-0)=30\ \text{kips}), acting at (x_c=7.5\ \text{ft}) from the left support. The support reactions must be:

- Left reaction: (R_A=22.5\ \text{kips})
- Right reaction: (R_B=7.5\ \text{kips})

Within the loaded interval, (V(x)=22.5-2x), so the shear is zero at (x=11.25\ \text{ft}). The maximum moment is:

\[
M(11.25)=22.5(11.25)-\frac{2}{2}(11.25)^2=126.5625\ \text{kip-ft}\approx126.6\ \text{kip-ft}
\]

Expected displayed maximum: **126.6 kip-ft at 11.25 ft**.

## Out of scope

- Cantilever, fixed, continuous, or otherwise statically indeterminate beams
- Multiple point loads or multiple distributed loads
- Load combinations, moving loads, or dynamic analysis
- Section capacity, stress, buckling, or design checks
- Deflection calculations
- Automatic section property lookup or structural code compliance
- Saving, exporting, or sharing analyses
