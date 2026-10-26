import math
import pytest
from src.atlas_rf.model import estimate_patch, back_to_front_ratio_db, C0_M_S


def test_wavelength_at_5ghz_is_about_60mm():
    est = estimate_patch(5e9, 3.48, 0.762e-3)
    assert est.free_space_wavelength_m == pytest.approx(C0_M_S / 5e9)
    assert est.free_space_wavelength_m * 1e3 == pytest.approx(59.96, rel=0.01)


def test_patch_dimensions_are_positive_and_reasonable():
    est = estimate_patch(5e9, 3.48, 0.762e-3)
    assert 0.015 < est.width_m < 0.025
    assert 0.010 < est.length_m < 0.020


def test_invalid_frequency_raises():
    with pytest.raises(ValueError):
        estimate_patch(0, 3.48, 0.762e-3)


def test_back_to_front_ratio():
    assert back_to_front_ratio_db(1.0, 0.01) == pytest.approx(-20.0)
    assert math.isinf(back_to_front_ratio_db(1.0, 0.0))
