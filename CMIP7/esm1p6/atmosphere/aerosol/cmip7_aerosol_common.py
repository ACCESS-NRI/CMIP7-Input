

def zero_poles(cube):
    # Polar values should have no longitude dependence
    # For aerosol emissions they should be zero
    latdim = cube.coord_dims('latitude')
    assert latdim == (1,)
    cube.data[:, 0] = 0.0
    cube.data[:, -1] = 0.0
