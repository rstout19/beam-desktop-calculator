"""Statically determinate beam calculations for partial uniform loads."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class BeamResults:
    left_reaction: float
    right_reaction: float
    positions: np.ndarray
    shear: np.ndarray
    moment: np.ndarray
    max_moment: float
    max_moment_x: float


def analyze_beam(span: float, loads, samples: int = 501) -> BeamResults:
    """Analyze a simply supported beam under (intensity, start, end) loads."""
    if not np.isfinite(span):
        raise ValueError("All numeric inputs must be finite.")
    if span <= 0:
        raise ValueError("Beam span must be greater than zero.")
    if not loads:
        raise ValueError("Add at least one distributed load.")
    for intensity, start, end in loads:
        if not all(np.isfinite(value) for value in (intensity, start, end)):
            raise ValueError("All numeric inputs must be finite.")
        if intensity < 0:
            raise ValueError("Uniform load cannot be negative.")
        if not (0 <= start < end <= span):
            raise ValueError("Each load must satisfy 0 ≤ start < end ≤ span.")
    if samples < 2:
        raise ValueError("At least two diagram samples are required.")

    load_resultants = [intensity * (end - start) for intensity, start, end in loads]
    load_centroids = [(start + end) / 2 for _, start, end in loads]
    right_reaction = sum(q * xc / span for q, xc in zip(load_resultants, load_centroids))
    total_load = sum(load_resultants)
    left_reaction = total_load - right_reaction

    x = np.linspace(0.0, span, samples)
    shear = np.full_like(x, left_reaction)
    moment = left_reaction * x
    boundaries = {0.0, span}
    for intensity, start, end in loads:
        shear -= intensity * np.maximum(0.0, np.minimum(x, end) - start)
        moment -= 0.5 * intensity * np.maximum(0.0, x - start) ** 2
        moment += 0.5 * intensity * np.maximum(0.0, x - end) ** 2
        boundaries.update((start, end))

    candidates = sorted(boundaries)
    # Between load boundaries shear is linear, so any interior moment extremum
    # occurs where the combined shear crosses zero in that interval.
    for left, right in zip(candidates, candidates[1:]):
        v_left = _shear_at(left, left_reaction, loads)
        v_right = _shear_at(right, left_reaction, loads)
        if v_left * v_right < 0:
            candidates.append(left + (right - left) * (-v_left) / (v_right - v_left))
    candidates = sorted(set(candidates))
    candidate_moments = [_moment_at(position, left_reaction, loads) for position in candidates]
    maximum_index = int(np.argmax(candidate_moments))

    return BeamResults(
        left_reaction=left_reaction,
        right_reaction=right_reaction,
        positions=x,
        shear=shear,
        moment=moment,
        max_moment=candidate_moments[maximum_index],
        max_moment_x=candidates[maximum_index],
    )


def _shear_at(position, left_reaction, loads):
    return left_reaction - sum(
        intensity * max(0.0, min(position, end) - start)
        for intensity, start, end in loads
    )


def _moment_at(position, left_reaction, loads):
    return left_reaction * position + sum(
        -0.5 * intensity * max(0.0, position - start) ** 2
        + 0.5 * intensity * max(0.0, position - end) ** 2
        for intensity, start, end in loads
    )
