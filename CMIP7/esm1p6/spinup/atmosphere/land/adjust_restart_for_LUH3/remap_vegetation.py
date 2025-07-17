import argparse
import yaml
import numpy
import xarray

def _parse_args():
    """Read the command line arguments."""

    parser = argparse.ArgumentParser(
            prog="remap_vegetation",
            description="Process the CABLE section of a UM7 restart " +\
                    "for a new vegetation map"
            )

    parser.add_argument(
            "-i",
            "--input",
            help="Reference CABLE section of UM7 restart to convert"
            )
    parser.add_argument(
            "-o",
            "--output",
            help="Name to write the new restart to"
            )
    parser.add_argument(
            "-m",
            "--vegetation_map",
            help="New vegetation map to use"
            )
    parser.add_argument(
            "-c",
            "--config",
            help="Config file to use for the remapping",
            )

    return parser.parse_args()
    
def prepare_mapping(nVeg, ConfigFile):
    """Read the configuration yaml file, validate it and apply defaults where
    necessary."""

    with open(ConfigFile, 'r') as conf:
        MappingConf = yaml.safe_load(conf)

    # At the moment, the only thing that requires defaults is the input to
    # output vegetation mapping. By default, it maps in a 1-to-1 manner, i.e.
    # vegetation type 1 in the old vegetation map maps to vegetation type 1 in
    # the new vegetation map.
    VegetationMapping = {i: [i] for i in range(nVeg)}

    # Apply the supplied mappings
    if 'vegetation_map' in MappingConf:
        for OutVegType, InVegTypes in MappingConf['vegetation_map'].items():
            # The user specified mappings are going to offset by -1, since in 
            # the Fortran world we use 1 based indexing and that's how people 
            # think about the vegetation types.
            VegetationMapping[OutVegType-1] = [InVeg-1 for InVeg in InVegTypes]
    
    MappingConf['vegetation_map'] = VegetationMapping

    # Apply the search defaults
    MappingConf['search_radius'] = MappingConf.get('search_radius', 2)
    MappingConf['latitude_band'] = MappingConf.get('latitude_band', 8)
    MappingConf['minimum_points'] = MappingConf.get('minimum_points', 1)
    
    return MappingConf

def setup_output_dataset(OutputVegetation, VariableList):
    """Use the OutputVegetation as a template to set up the Dataset that will
    contain the new restart information. Use the list of variable names
    contained in the Config to set the NetCDF variable names."""

    # Set the fill value that we will use for all variables
    FillVal = 1e20

    # Get the shape of the output data to perform validation
    nOutputVeg, nLat, nLon = OutputVegetation.shape

    # Set up the new xarray dataset to write to
    Longitudes = numpy.linspace(0.0, 360.0, nLon, endpoint=False)
    Latitudes = numpy.linspace(-90.0, 90.0, nLat, endpoint=True)
    VegTypes = numpy.arange(1, nOutputVeg+1)

    # I couldn't make the xarray.Dataset call accept a dictionary generator as
    # an argument for data_vars. So initialise the Dataset, then add variables
    # to it later.
    OutDataset = xarray.Dataset(
            coords={
                'lon': Longitudes,
                'lat': Latitudes,
                'veg': VegTypes
                }
            )

    # Add the variables now
    for Variable in VariableList:
        OutDataset[Variable] = (
                    ('veg', 'lat', 'lon'),
                    numpy.full(
                        (nOutputVeg, nLat, nLon),
                        FillVal,
                        dtype=numpy.float32
                        )
                    )
        OutDataset[Variable].encoding['_FillValue'] = FillVal

    return OutDataset
                    
def modify_mask_for_cell(SearchMask, GridCell, Coord):
    """Modify the input search mask to only include the current grid cell at
    Coord."""

    Lon, Lat = Coord
    SearchMask[Lat, Lon] = True

def modify_mask_for_nearest(SearchMask, SearchRadius, Coord):
    """Modify the input search mask to only include the specified 'radius' of
    points around the given Coord. In this instance, radius is just a block of
    points with index +-SearchRadius around the original Coord."""
    
    # Destructure for more readable usage later
    Lon, Lat = Coord
    nLat, nLon = SearchMask.shape

    # Create the set of coordinates to unmask
    SearchInds = numpy.arange(-SearchRadius, SearchRadius+1)

    # Clip the latitude indices, since they aren't periodic
    LatInds = numpy.clip(Lat + SearchInds, 0, nLat-1)

    # Apply mod to longitude indices, since they are periodic
    LonInds = numpy.mod(Lon + SearchInds, nLon)

    # Modify the mask in place
    for LatSearch in LatInds:
        for LonSearch in LonInds:
            SearchMask[LatSearch, LonSearch] = True

def modify_mask_for_latitude_band(SearchMask, LatitudeBand, Coord):
    """Modify the input search mask to only include the specifed band of
    latitudes around the given Coord."""

    # Destructure for more readable usage later
    Lon, Lat = Coord
    nLat, nLon = SearchMask.shape

    # Create the set of coordinates to unmask
    SearchInds = numpy.arange(-LatitudeBand, LatitudeBand+1)

    # Clip the latitude indices, since they aren't periodic
    LatInds = numpy.clip(Lat + SearchInds, 0, nLat-1)

    # Modify the mask in place
    for LatSearch in LatInds:
        SearchMask[LatSearch, :] = True

def modify_mask_for_global(SearchMask, Global, Coord):
    """Modify the input search mask to include the whole globe. Include
    arguments for consistency with the other masking methods."""

    # Nothing interesing to do here
    SearchMask[:] = True

def find_active_tiles(SearchMask, InputVegetation, VegetationMapping):
    """Using the supplied search mask, generate a set of masks which are an OR
    of the original search mask and a mask describing the active tiles, defined
    as a tile with an area fraction of greater than 1e-3. Generates a mask for
    each of the vegetation types used to construct the new vegetation type."""

    # Make it a list, because there are instances where more than 1 input
    # vegetation type maps to a single output vegetation type
    ActiveTileMasks = []

    for VegType in VegetationMapping:
        # The search mask should then be a logical and of:
        # * The land points (where the vegetation is non nan)
        # * The supplied search mask
        # * The tiles which have a vegetation type greater than 0.0
        # Note that the minimum area threshold is chosen carefully to be
        # greater than 1e-6, which is the value used for tiles that will become
        # active in future due to land use change
        TileSearchMap = ~numpy.isnan(InputVegetation[VegType, :, :]) &\
                SearchMask & (InputVegetation[VegType, :, :] > 1e-7)

        ActiveTileMasks.append(TileSearchMap)

    return ActiveTileMasks

def remap_vegetation(InputDataset, InputVegetation, OutputVegetation, Config):
    """Map the input vegetation to the output vegetation."""

    # Read in the variable mappings- needs number of vegetation types for map
    nOutputVeg, nLat, nLon = OutputVegetation.shape
    MappingConf = prepare_mapping(nOutputVeg, Config)

    # Destructure the configuration variables
    PerCellVariables = MappingConf['per_cell']
    PerTileVariables = MappingConf['per_tile']
    VegMapping = MappingConf['vegetation_map']
    SearchRadius = MappingConf['search_radius']
    LatitudeBand = MappingConf['latitude_band']
    MinPointsFound = MappingConf['minimum_points']
    
    # Set up the Dataset we're going to write to
    OutDataset = setup_output_dataset(OutputVegetation, PerCellVariables +
                                      PerTileVariables)

    # Add the land fractions- also include previous year as same for LUC
    OutDataset['FRACTIONS OF SURFACE TYPES'] = (('veg', 'lat', 'lon'),
                                               NewVegetation)
    OutDataset['PREVIOUS YEAR SURF FRACTIONS (TILES)'] =
        (('veg', 'lat', 'lon'), NewVegetation)

    # Perform the per-cell averaging
    # Apply a mask to the array, so we don't mess up our summations with
    # near-zero vegetation fractions
    InputVegetation = numpy.ma.masked_less(InputVegetation, 1e-3)

    for Variable in PerCellVariables:
        res = numpy.sum(InputDataset[Variable].to_numpy() * InputVegetation, axis=0)
        OutDataset[Variable] = (
                ('veg', 'lat', 'lon'),
                numpy.repeat(res[numpy.newaxis, :, :], nOutputVeg, axis=0)
                )

    # Perform the per-tile averaging
    # To only iterate over desired points, we can mask the array where the
    # array is nan (which correspond to ocean points). Then use
    # numpy.ma.ndenumerate to only iterate over the land points. This will
    # include tiles with 0.0 vegetation fraction.
    MaskedOutputVeg = numpy.ma.masked_invalid(OutputVegetation)

    # At each point, we're going to use a new mask to assist the search. But we
    # don't want to allocate a new array every point- initialise a mask here,
    # and then modify the mask in place.
    SearchMask = numpy.full((nLat, nLon), False, dtype=bool)

    # Set up the set of search methods and search parameters to walk through
    SearchMethods = [
            modify_mask_for_cell,
            modify_mask_for_nearest,
            modify_mask_for_latitude_band,
            modify_mask_for_global
            ]

    # The cell and global searches take no parameters
    SearchParams = [None, SearchRadius, LatitudeBand, None]

    # The minimum number of points permitted for a search to be successful
    PointsThreshold = [1, MinPointsFound, MinPointsFound, 1]

    # Start by iterating through each output vegetation type
    for (OutVeg, Lat, Lon), _ in numpy.ma.ndenumerate(MaskedOutputVeg):

        # Iterate through the search methods until a success
        for Method, Param, MinPoints in zip(SearchMethods, SearchParams,
                                            PointsThreshold):
            Method(SearchMask, Param, (Lon, Lat))

            # Further refine the mask to only include the active tiles
            ActiveTileMasks = find_active_tiles(
                    SearchMask,
                    InputVegetation,
                    VegMapping[OutVeg]
                    )

            # Check how many valid points there are in the mask
            PointsFound = sum([ActiveTileMask.sum() for ActiveTileMask in
                              ActiveTileMasks])

            if PointsFound >= MinPoints:
                # Search was successful
                break

        # Now we can continue with a generic masked find and average
        # There are some veg types that don't have any values anywhere
        # In that case, just use zeros everywhere.
        if PointsFound < MinPointsFound:
            for Variable in PerTileVariables:
                OutDataset[Variable][OutVeg, Lat, Lon] = 0.0
        else:
            for Variable in PerTileVariables:
                # Set incrementing value to 0
                Total = 0.0
                print(f"Converting variable {Variable}")

                # We want to summate over all active tiles then average by the
                # number of active tiles. In most cases, this only involves one
                # vegetation type, but sometimes there are more.
                for (InVeg, TileMask) in \
                        zip(VegMapping[OutVeg], ActiveTileMasks):
                    # Turn the data into a numpy array, then index it with the
                    # generated mask.
                    VarData = InputDataset[Variable][InVeg, :, :].to_numpy()
                    TotalForVegType = VarData[TileMask].sum()
                    Total += TotalForVegType

                # Average and set the index in the dataarray.
                OutDataset[Variable][OutVeg, Lat, Lon] =\
                        Total / PointsFound

        # Reset the search mask to false
        SearchMask[:] = False

    # Finally set the 
    return OutDataset

if __name__ == '__main__':

    # Process command line args
    args = _parse_args()
    OrigDataset = xarray.open_dataset(args.input)
    OrigVegetation = OrigDataset['FRACTIONS OF SURFACE TYPES'].to_numpy()
    NewVegetation = xarray.open_dataset(args.vegetation_map)
    NewVegetation = NewVegetation['fraction'][0, :, :, :].to_numpy()

    OutDataset = remap_vegetation(
            OrigDataset,
            OrigVegetation,
            NewVegetation,
            args.config
            )

    OutDataset.to_netcdf(args.output)
