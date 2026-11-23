# Simply Supported Beam Calculator

## Purpose

A Python desktop application for analyzing a simply supported beam under one or more uniform distributed loads. It reports support reactions and the maximum bending moment, and plots the beam's shear and moment diagrams.

## Platform

- Python desktop app using Tkinter, started with `python app.py`.
- Keep calculations in their own module, separate from the window code.
- Use NumPy for numerical calculations and Matplotlib for diagrams embedded in the Tkinter window.

## Model and assumptions

- The beam is straight, prismatic, and simply supported at (x=0) and (x=L).
- The beam span (L) is measured in feet.
- The beam section is identified by a text label such as `W18x35`. The label is informational; section strength, deflection, and self-weight calculations are outside this calculator's scope.
- A deflection limit in inches may be recorded as a design note. This version does not calculate deflection or check the limit.
- Each downward uniform distributed load (i), with intensity (w_i), acts from position (a_i) to position (b_i), where (0 \le a_i < b_i \le L). Loads may overlap.
- Use kip for force, kip/ft for distributed load, and kip-ft for moment.
- Use static equilibrium with the usual sign convention: positive support reactions act upward, positive shear is upward on the left face, and positive sagging moment is plotted above the axis.

## Inputs

| Input | Units | Meaning |
|---|---|---|
| Beam span, (L) | ft | Distance between supports |
| Beam section | — | Descriptive label, for example `W18x35` |
| Deflection limit | in | Optional design note saved with the beam; not checked by calculations |
| Uniform load, (w_i) | kip/ft | Downward load intensity for each load row |
| Load start, (a_i) | ft | Start position of that load, measured from the left support |
| Load end, (b_i) | ft | End position of that load, measured from the left support |

Provide editable numeric controls with units shown beside their labels and allow users to add or remove load rows, keeping at least one row. Give each load a distinct color and use that color consistently in its beam schematic representation. The section label is free text. Numeric inputs must be finite; require (L>0), (w_i\ge0), and (0\le a_i<b_i\le L) for every load. A supplied deflection limit must be a finite positive number. Reject invalid or empty required input, explain the constraint, and do not display results calculated from invalid values.

## Save and open

Provide a File menu with Save and Open commands. Save the support type (`simply_supported`), span, section label, optional deflection limit, and every load's intensity, start, and end to a JSON file. Open must restore all saved values and load rows. Handle unreadable or malformed files with a clear error message and leave the current beam unchanged. The support type is stored explicitly even though only simply supported beams are currently supported.

## Calculations

For each load (i), let (Q_i=w_i(b_i-a_i)) be its resultant, acting at centroid (x_{c,i}=(a_i+b_i)/2). Use superposition to combine the loads.

Calculate the reactions from equilibrium:

\[
 R_B=\frac{\sum_i Q_i x_{c,i}}{L}, \qquad R_A=\sum_i Q_i-R_B
\]

For positions (0\le x\le L), calculate shear and bending moment using the load intensity active between (a) and (b):

\[
V(x)=R_A-\sum_i w_i\max\left(0,\min(x,b_i)-a_i\right)
\]

\[
M(x)=R_Ax+\sum_i\left[-\frac{w_i}{2}\max(0,x-a_i)^2+\frac{w_i}{2}\max(0,x-b_i)^2\right]
\]

The formulas must also work when loads start after the left support, end before the right support, or overlap. Find the maximum positive bending moment over the span and report its location. Check load boundaries and support locations, plus any zero-shear location within each interval between load boundaries. For zero total load, report zero maximum moment at the supports.

Do not round values used in calculations. Round only for display: reactions and load intensity to a sensible number of decimals, and maximum moment and its location to one decimal place by default.

## Outputs

- Left and right support reactions, (R_A) and (R_B), in kips.
- Maximum positive bending moment in kip-ft and its position in feet from the left support.
- A beam schematic showing the supports, span, section label, and each distributed load's extent and direction in its distinct color.
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
- Multiple point loads
- Load combinations, moving loads, or dynamic analysis
- Section capacity, stress, buckling, or design checks
- Deflection calculations
- Automatic section property lookup or structural code compliance
- Exporting or sharing analyses
