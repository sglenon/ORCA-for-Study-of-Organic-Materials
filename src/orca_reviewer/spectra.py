from __future__ import annotations

import numpy as np

HC_EV_NM = 1239.841984


def gaussian_broaden(x, positions, intensities, fwhm):
    """Return a Gaussian-broadened spectrum on grid x."""
    x = np.asarray(x, dtype=float)
    positions = np.asarray(positions, dtype=float)
    intensities = np.asarray(intensities, dtype=float)
    if fwhm <= 0:
        raise ValueError("fwhm must be positive")
    sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
    y = np.zeros_like(x)
    for pos, inten in zip(positions, intensities):
        y += inten * np.exp(-0.5 * ((x - pos) / sigma) ** 2)
    return y


def energy_to_wavelength(energy_ev):
    energy_ev = np.asarray(energy_ev, dtype=float)
    if np.any(energy_ev <= 0):
        raise ValueError("energy must be positive")
    return HC_EV_NM / energy_ev


def wavelength_to_energy(wavelength_nm):
    wavelength_nm = np.asarray(wavelength_nm, dtype=float)
    if np.any(wavelength_nm <= 0):
        raise ValueError("wavelength must be positive")
    return HC_EV_NM / wavelength_nm
