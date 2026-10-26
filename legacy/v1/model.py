"""First-order analytical model for a rectangular microstrip patch.

This is a design-estimation model, not a full-wave electromagnetic solver.
Dimensions use SI units throughout.
"""
from dataclasses import dataclass
import math

C0_M_S = 299_792_458.0


@dataclass(frozen=True)
class PatchEstimate:
    frequency_hz: float
    width_m: float
    effective_permittivity: float
    effective_length_m: float
    length_m: float
    free_space_wavelength_m: float


def estimate_patch(frequency_hz: float, eps_r: float, substrate_height_m: float) -> PatchEstimate:
    """Estimate rectangular patch dimensions using common closed-form equations.

    Assumptions: thin substrate relative to wavelength, dominant TM10-like mode,
    isotropic substrate, negligible copper roughness and manufacturing variation.
    """
    if frequency_hz <= 0:
        raise ValueError("frequency_hz must be positive")
    if eps_r <= 1:
        raise ValueError("eps_r must be greater than 1")
    if substrate_height_m <= 0:
        raise ValueError("substrate_height_m must be positive")

    wavelength = C0_M_S / frequency_hz
    width = (C0_M_S / (2 * frequency_hz)) * math.sqrt(2 / (eps_r + 1))
    eps_eff = ((eps_r + 1) / 2) + ((eps_r - 1) / 2) * (
        1 / math.sqrt(1 + 12 * substrate_height_m / width)
    )
    length_eff = C0_M_S / (2 * frequency_hz * math.sqrt(eps_eff))
    ratio = width / substrate_height_m
    delta_l = 0.412 * substrate_height_m * (
        ((eps_eff + 0.3) * (ratio + 0.264))
        / ((eps_eff - 0.258) * (ratio + 0.8))
    )
    length = length_eff - 2 * delta_l
    if length <= 0:
        raise ValueError("Estimated patch length is non-positive; check inputs")
    return PatchEstimate(
        frequency_hz=frequency_hz,
        width_m=width,
        effective_permittivity=eps_eff,
        effective_length_m=length_eff,
        length_m=length,
        free_space_wavelength_m=wavelength,
    )


def cosine_power_pattern(theta_rad, exponent: float = 8.0):
    """Illustrative broadside pattern proxy; NOT a validated patch radiation solution.

    theta is angle from the +Y boresight. Returns normalized field amplitude.
    """
    import numpy as np
    theta = np.asarray(theta_rad, dtype=float)
    return np.clip(np.cos(theta), 0.0, None) ** exponent


def back_to_front_ratio_db(front_power: float, back_power: float) -> float:
    """Return 10*log10(back/front); values below 0 dB indicate less back power."""
    if front_power <= 0 or back_power < 0:
        raise ValueError("front_power must be positive and back_power non-negative")
    if back_power == 0:
        return float("-inf")
    return 10 * math.log10(back_power / front_power)
