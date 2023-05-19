from pathlib import Path
import pytest
from astropy import units as u
import numpy as np
import matplotlib.pyplot as plt

import netCDF4 as nc
from os import chdir
    
from VSPEC.waccm.read_nc import validate_variables, get_time_index, time_unit,get_shape
import VSPEC.waccm.read_nc as rw

chdir(Path(__file__).parent)

DATA_PATH = Path('/Users/tjohns39/Documents/GCMs/WACCM/TR1e_flare_1yr_psg.nc')


def read_TR1():
    path = Path('/Users/tjohns39/Documents/GCMs/WACCM/TR1e_flare_1yr_psg.nc')
    with nc.Dataset(path,'r',format='NETCDF4') as data:
        validate_variables(data)
        0

def test_validate_vars():
    with nc.Dataset(DATA_PATH,'r',format='NETCDF4') as data:
        validate_variables(data)

def test_get_time_index():
    with nc.Dataset(DATA_PATH,'r',format='NETCDF4') as data:
        time = np.array(data.variables['time'][:])*time_unit
        for i,t in enumerate(time):
            assert get_time_index(data,t) == i

def test_get_shape():
    with nc.Dataset(DATA_PATH,'r',format='NETCDF4') as data:
        shape = get_shape(data)
        assert data.variables['T'].shape == shape

def test_surface_pressure():
    with nc.Dataset(DATA_PATH,'r',format='NETCDF4') as data:
        ps = rw.get_psurf(data,0)
        _,_,N_lat,N_lon = get_shape(data)
        assert ps.shape == (N_lat,N_lon)
def test_pressure():
    with nc.Dataset(DATA_PATH,'r',format='NETCDF4') as data:
        press = rw.get_pressure(data,0)
        _,N_layer,N_lat,N_lon = get_shape(data)
        assert press.shape == (N_layer,N_lat,N_lon)



if __name__ in '__main__':

    # read_TR1()
    # test_validate_vars()
    # test_get_time_index()
    # test_get_shape()
    test_surface_pressure()
    test_pressure()

