#!/usr/bin/env python

"""
Tests for `VSPEC.helpers` module
"""
from os import system

from astropy import units as u
import numpy as np
import pytest
from time import sleep,time

from VSPEC import helpers
from VSPEC.geometry import SystemGeometry


def test_to_float():
    """
    Test `to_float()`

    Run tests for `VSPEC.helpers.to_float()`
    This function converts `astropy.Quantity` objects to `float`
    given a target unit
    """
    quant = 1*u.um
    unit = u.AA
    # Angstrom = 1e-10 m
    # micron = 1e-6 m
    # 1e4 angstrom / micron
    expected = 1e4
    observed = helpers.to_float(quant, unit)
    message = f'Units converted unsuccessfully. Expected: {expected}, Observed: {observed}'
    assert observed == pytest.approx(
        expected, rel=1e-9), 'test failed: ' + message

    quant = 1*u.um
    unit = u.Unit('')  # dimensionless
    try:
        helpers.to_float(quant, unit)
        assert False, 'test failed: Bad unit conversion did not raise error'
    except u.UnitConversionError:
        pass


def test_isclose():
    """
    Test `is_close()`

    Run tests for `VSPEC.helpers.isclose()`
    This function extends the `numpy.isclose()` function to
    support `astropy.units.Quantity` objects
    """
    param1 = np.linspace(0, 4, 5)*u.m
    param2 = np.linspace(0, 4, 5)*u.m
    tol = 0*u.m
    assert np.all(helpers.isclose(param1, param2, tol)), 'test failed'

    param1 = np.linspace(0, 4, 5)*u.m
    param2 = (np.linspace(0, 4, 5) + 1e-5)*u.m
    tol = 1e-4*u.m
    assert np.all(helpers.isclose(param1, param2, tol)), 'test failed'

    param1 = np.linspace(0, 4, 5)*u.m
    param2 = (np.linspace(0, 4, 5) + 1e-5)*u.m
    tol = 1e-6*u.m
    assert not np.all(helpers.isclose(param1, param2, tol)), 'test failed'

    param1 = np.linspace(0, 4, 5)*u.m
    param2 = (np.linspace(0, 4, 5) + 1e-5)*u.m
    tol = 1e-5*u.m  # boundary case
    assert np.all(helpers.isclose(param1, param2, tol)), 'test failed'

    param1 = np.linspace(0, 4, 5)*u.m
    param2 = (np.linspace(0, 400, 5))*u.cm
    tol = 1e-6*u.m
    assert np.all(helpers.isclose(param1, param2, tol)), 'test failed'

    param1 = np.linspace(0, 4, 5)*u.m
    param2 = (np.linspace(0, 4, 5))*u.cm
    tol = 1e-6*u.m
    assert not np.all(helpers.isclose(param1, param2, tol)), 'test failed'

    param1 = np.linspace(0, 4, 5)*u.m
    param2 = (np.linspace(0, 4, 5))*u.day
    tol = 1e-6*u.m
    try:
        np.all(helpers.isclose(param1, param2, tol))
        assert False, 'test failed'
    except u.UnitConversionError:
        pass

    param1 = np.linspace(0, 4, 5)*u.m
    param2 = (np.linspace(0, 4, 5))*u.m
    tol = 1e-6*u.s
    try:
        np.all(helpers.isclose(param1, param2, tol))
        assert False, 'test failed'
    except u.UnitConversionError:
        pass

    param1 = np.linspace(0, 4, 5)*u.m
    param2 = (np.linspace(0, 4, 5))*u.m
    tol = 1e-6*u.cm
    try:
        np.all(helpers.isclose(param1, param2, tol))
    except u.UnitConversionError:
        assert False, 'test failed'


def test_get_transit_radius():
    """
    Test `get_transit_radius()`

    Run tests for VSPEC.helpers.get_transit_radius()
    This function calculates the minimum radius from mid-transit
    (i.e. phase=180, i=90 deg) that a planet must be to have no
    overlap between the planetary disk and stellar disk.
    """
    # Use parameters for GJ 1214 b
    # Taken from NExSci Archive on
    # 2022-03-03 by Ted Johnson
    system_distance = 14.6427*u.pc
    stellar_radius = 0.215*u.R_sun
    semimajor_axis = 0.01490*u.AU
    planet_radius = 2.742*u.R_earth
    transit_duration = 0.8788*u.hr
    orbital_period = 1.58040433*u.day
    true_radius = np.pi*u.rad * \
        helpers.to_float(transit_duration/orbital_period,
                         u.dimensionless_unscaled)
    predicted_radius = helpers.get_transit_radius(system_distance,
                                                  stellar_radius,
                                                  semimajor_axis,
                                                  planet_radius)
    true_radius = helpers.to_float(true_radius, u.deg)
    predicted_radius = helpers.to_float(predicted_radius, u.deg)
    message = f'True: {true_radius:.2f}, Calculated: {predicted_radius:.2f}'
    assert predicted_radius == pytest.approx(
        true_radius, rel=0.1), 'test failed: ' + message

def test_is_port_in_use():
    """
    Test `VSPEC.is_port_in_use`
    """
    default_psg_port = 3000
    timeout_duration = 10 # timeout after 10s
    system('docker start psg')
    timeout = time() + timeout_duration
    while True:
        if helpers.is_port_in_use(default_psg_port):
            break
        elif time() > timeout:
            raise RuntimeError('Test failed -- timeout')
    system('docker stop psg')
    timeout = time() + timeout_duration
    while True:
        if not helpers.is_port_in_use(default_psg_port):
            break
        elif time() > timeout:
            raise RuntimeError('Test failed -- timeout')

def test_arrange_teff():
    """
    Test `VSPEC.helpers.arrange_teff`
    """
    teff1 = 3010*u.K
    teff2 = 3090*u.K
    assert np.all(helpers.arrange_teff(teff1,teff2) == [3000,3100]*u.K)

    teff1 = 3000*u.K
    teff2 = 3100*u.K
    assert np.all(helpers.arrange_teff(teff1,teff2) == [3000,3100]*u.K)

    teff1 = 2750*u.K
    teff2 = 3300*u.K
    assert np.all(helpers.arrange_teff(teff1,teff2) == [27,28,29,30,31,32,33]*(100*u.K))

def test_get_surrounding_teffs():
    """
    Test `VSPEC.helpers.arrange_teff`
    """
    Teff = 3050*u.K
    low,high = helpers.get_surrounding_teffs(Teff)
    assert low == 3000*u.K
    assert high == 3100*u.K

    with pytest.raises(ValueError):
        Teff = 3000*u.K
        helpers.get_surrounding_teffs(Teff)

def test_plan_to_df():
    geo = SystemGeometry()
    plan = geo.get_observation_plan(0*u.deg,10*u.day,N_obs=10)
    df = helpers.plan_to_df(plan)
    for key in plan.keys():
        assert np.any(df.columns.str.contains(key))


if __name__ in '__main__':
    test_to_float()
    test_isclose()
    test_get_transit_radius()
    test_is_port_in_use()
    test_arrange_teff()
    test_plan_to_df()