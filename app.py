"""Tkinter interface for the simply supported beam calculator."""

import tkinter as tk
from tkinter import ttk

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from beam_calculations import analyze_beam


class BeamCalculator:
    LOAD_COLORS = ["#d17a22", "#7b61a8", "#008b8b", "#c44e52", "#4c72b0", "#8172b2"]

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Beam Calculator")
        root.geometry("1120x760")
        root.minsize(900, 620)

        self.vars = {
            "span": tk.StringVar(value="30"),
            "section": tk.StringVar(value="W18x35"),
        }
        self.loads = []
        self._build_layout()
        self._update_results()

    def _build_layout(self) -> None:
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        left = ttk.Frame(self.root, padding=18)
        left.grid(row=0, column=0, sticky="nsw")
        left.columnconfigure(0, weight=1)
        right = ttk.Frame(self.root, padding=(4, 18, 18, 18))
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(2, weight=1)

        ttk.Label(left, text="Simply Supported Beam", font=("TkDefaultFont", 16, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 6))
        ttk.Label(left, text="Beam span (ft)").grid(row=1, column=0, sticky="w", pady=(4, 2))
        ttk.Entry(left, textvariable=self.vars["span"], width=12).grid(row=2, column=0, sticky="w")
        self.vars["span"].trace_add("write", self._on_input_change)
        ttk.Label(left, text="Section label").grid(row=3, column=0, sticky="w", pady=(8, 2))
        ttk.Entry(left, textvariable=self.vars["section"], width=20).grid(row=4, column=0, sticky="w")
        self.vars["section"].trace_add("write", self._on_input_change)

        ttk.Label(left, text="Uniform distributed loads", font=("TkDefaultFont", 11, "bold")).grid(
            row=5, column=0, sticky="w", pady=(18, 5))
        ttk.Label(left, text="Color   kip/ft     start ft     end ft", foreground="#586579").grid(
            row=6, column=0, sticky="w")
        self.load_rows = ttk.Frame(left)
        self.load_rows.grid(row=7, column=0, sticky="ew")
        self.add_load_button = ttk.Button(left, text="+ Add load", command=self._add_load)
        self.add_load_button.grid(row=8, column=0, sticky="w", pady=(8, 0))
        self._add_load("2", "0", "15", update=False)

        self.error_var = tk.StringVar()
        ttk.Label(left, textvariable=self.error_var, foreground="#b42318",
                  wraplength=270).grid(row=9, column=0, sticky="w", pady=(12, 0))
        ttk.Label(left, text="Positive load acts downward. Include beam self-weight in the load if needed.",
                  wraplength=250, foreground="#586579").grid(
            row=10, column=0, sticky="w", pady=(10, 0))

        ttk.Label(right, text="Analysis results", font=("TkDefaultFont", 16, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 12))
        summary = ttk.Frame(right)
        summary.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.result_vars = {
            "left": tk.StringVar(), "right": tk.StringVar(), "moment": tk.StringVar()
        }
        for column, (key, title) in enumerate([
            ("left", "Left reaction"), ("right", "Right reaction"), ("moment", "Maximum moment")
        ]):
            card = ttk.LabelFrame(summary, text=title, padding=10)
            card.grid(row=0, column=column, sticky="ew", padx=(0, 8))
            ttk.Label(card, textvariable=self.result_vars[key], font=("TkDefaultFont", 12, "bold")).pack()
            summary.columnconfigure(column, weight=1)

        self.figure = Figure(figsize=(7.5, 6), dpi=100, constrained_layout=True)
        self.beam_ax = self.figure.add_subplot(3, 1, 1)
        self.shear_ax = self.figure.add_subplot(3, 1, 2)
        self.moment_ax = self.figure.add_subplot(3, 1, 3)
        self.canvas = FigureCanvasTkAgg(self.figure, master=right)
        self.canvas.get_tk_widget().grid(row=2, column=0, sticky="nsew")

    def _add_load(self, intensity="", start="", end="", update=True) -> None:
        index = len(self.loads)
        color = self.LOAD_COLORS[index % len(self.LOAD_COLORS)]
        load = {
            "intensity": tk.StringVar(value=intensity),
            "start": tk.StringVar(value=start),
            "end": tk.StringVar(value=end),
            "color": color,
        }
        self.loads.append(load)
        row = ttk.Frame(self.load_rows)
        row.grid(row=index, column=0, sticky="w", pady=2)
        ttk.Label(row, text="●", foreground=color).grid(row=0, column=0, padx=(0, 5))
        for column, key in enumerate(("intensity", "start", "end"), start=1):
            ttk.Entry(row, textvariable=load[key], width=8).grid(row=0, column=column, padx=(0, 4))
            load[key].trace_add("write", self._on_input_change)
        remove = ttk.Button(row, text="×", width=2,
                            command=lambda item=load: self._remove_load(item))
        remove.grid(row=0, column=4)
        load["row"] = row
        if update and hasattr(self, "result_vars"):
            self._update_results()

    def _remove_load(self, load) -> None:
        if len(self.loads) == 1:
            self.error_var.set("At least one distributed load is required.")
            return
        self.loads.remove(load)
        self._refresh_load_rows()
        self._update_results()

    def _refresh_load_rows(self) -> None:
        for child in self.load_rows.winfo_children():
            child.destroy()
        old = self.loads
        self.loads = []
        for item in old:
            self._add_load(item["intensity"].get(), item["start"].get(), item["end"].get(), update=False)

    def _on_input_change(self, *_args) -> None:
        self.root.after_idle(self._update_results)

    def _update_results(self) -> None:
        try:
            span = float(self.vars["span"].get())
            loads = [(float(item["intensity"].get()), float(item["start"].get()),
                      float(item["end"].get())) for item in self.loads]
            result = analyze_beam(span, loads)
        except ValueError as exc:
            self.error_var.set(str(exc) if str(exc) else "Enter valid numeric values for all fields.")
            for variable in self.result_vars.values():
                variable.set("—")
            for axis in (self.beam_ax, self.shear_ax, self.moment_ax):
                axis.clear()
            self.canvas.draw_idle()
            return

        self.error_var.set("")
        self.result_vars["left"].set(f"{result.left_reaction:.2f} kip")
        self.result_vars["right"].set(f"{result.right_reaction:.2f} kip")
        self.result_vars["moment"].set(
            f"{result.max_moment:.1f} kip-ft at {result.max_moment_x:.2f} ft")
        self._draw_diagrams(span, loads, result)

    def _draw_diagrams(self, span, loads, result) -> None:
        section = self.vars["section"].get().strip() or "Unspecified section"
        self.beam_ax.clear()
        self.shear_ax.clear()
        self.moment_ax.clear()

        self.beam_ax.plot([0, span], [0, 0], color="#26364a", linewidth=3)
        self.beam_ax.scatter([0, span], [0, 0], marker="^", s=100, color="#3e73b3", zorder=3)
        self.beam_ax.annotate(f"RA {result.left_reaction:.2f} kip", (0, 0.12), ha="left")
        self.beam_ax.annotate(f"RB {result.right_reaction:.2f} kip", (span, 0.12), ha="right")
        load_height = 0.8
        for index, ((intensity, start, end), item) in enumerate(zip(loads, self.loads)):
            color = item["color"]
            height = load_height + index * 0.55
            arrow_x = np.linspace(start, end, 7)
            self.beam_ax.quiver(arrow_x, np.full_like(arrow_x, height), np.zeros_like(arrow_x),
                                np.full_like(arrow_x, -0.42), angles="xy", scale_units="xy",
                                scale=1, color=color, width=0.004)
            self.beam_ax.plot([start, end], [height + 0.03, height + 0.03], color=color, linewidth=1.5)
            self.beam_ax.text((start + end) / 2, height + 0.10,
                              f"L{index + 1}: {intensity:g} kip/ft", ha="center", color=color, fontsize=8)
        self.beam_ax.set_title(f"Beam and loading — {section}", loc="left", fontsize=10)
        self.beam_ax.set_xlim(-0.04 * span, span * 1.04)
        self.beam_ax.set_ylim(-0.4, load_height + len(loads) * 0.55 + 0.45)
        self.beam_ax.set_yticks([])
        self.beam_ax.set_xlabel("Position from left support (ft)")
        self.beam_ax.grid(axis="x", alpha=0.2)

        self.shear_ax.plot(result.positions, result.shear, color="#3e73b3", linewidth=2)
        self.shear_ax.axhline(0, color="#536174", linewidth=0.8)
        self.shear_ax.set_ylabel("Shear (kip)")
        self.shear_ax.grid(alpha=0.2)

        self.moment_ax.plot(result.positions, result.moment, color="#1f7a50", linewidth=2)
        self.moment_ax.axhline(0, color="#536174", linewidth=0.8)
        self.moment_ax.scatter([result.max_moment_x], [result.max_moment], color="#d17a22", zorder=3)
        self.moment_ax.annotate(f"{result.max_moment:.1f} kip-ft at {result.max_moment_x:.2f} ft",
                                (result.max_moment_x, result.max_moment), xytext=(6, 8),
                                textcoords="offset points", fontsize=8)
        self.moment_ax.set_ylabel("Moment (kip-ft)")
        self.moment_ax.set_xlabel("Position from left support (ft)")
        self.moment_ax.grid(alpha=0.2)
        self.canvas.draw_idle()


def main() -> None:
    root = tk.Tk()
    BeamCalculator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
