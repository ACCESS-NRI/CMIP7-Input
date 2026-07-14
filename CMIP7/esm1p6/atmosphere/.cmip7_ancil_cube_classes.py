import iris
from iris.util import equalise_attributes, unify_time_units


class Cmip7Cube:
    def __init__(self, filepaths, constraint):
        self.filepaths = filepaths
        if isinstance(filepaths, Path):
           self.cube = iris.load_cube(filepaths, constraint)
        elif isinstance(filepaths, list):
            cube_list = iris.load_raw(filepath_list, constraint)
            equalise_attributes(cube_list)
            unify_time_units(cube_list)
            self.cube = cube_list.concatenate_cube()
        else:
            raise TypeError("Cmip7Cube expects a Path or a list of Paths")

    def __call__(self):
        return cube

    def zero_poles(self):
        # Polar values should have no longitude dependence
        # For aerosol emissions they should be zero
        cube = self.cube
        latdim = cube.coord_dims("latitude")
        assert latdim == (1,)
        cube.data[:, 0] = 0.0
        cube.data[:, -1] = 0.0
