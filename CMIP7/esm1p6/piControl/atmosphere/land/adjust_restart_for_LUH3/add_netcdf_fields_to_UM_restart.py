import xarray
import mule
import six

def modify_UM_field_by_name(FieldsFile, Dataset, VarName):
    """Take the DataArray attached to Dataset[VarName] and map it to the
    equivalent field in the UM fields file."""

    # We will want to check against the original FieldsFile field, to ensure
    # matching sizes
    VariableData = Dataset[VarName].to_numpy()
    nVeg, nLat, nLon = VariableData.shape

    # Retrieve the stash code
    UMName = VarName.replace('(', '\(').replace(')', '\)')
    # A little catch for the "/" for " PER " replacement
    try:
        StashCode = list(FieldsFile.stashmaster.by_regex(UMName).values())[0].item
    except:
        print(f"Finding {UMName} failed; try again replacing PER")
        UMName = UMName.replace(' PER ', '/')
        StashCode = list(FieldsFile.stashmaster.by_regex(UMName).values())[0].item

    # Check that the number of fields is the same as the vegetation dimension
    nFields = 0
    for Field in FieldsFile.fields:
        if Field.lbuser4 == StashCode:
            nFields += 1

    assert nFields == nVeg

    # Iterate through tiles
    Tile = 0
    for Field in FieldsFile.fields:
        if Field.lbuser4 == StashCode:
            OrigData = Field.get_data()
            NewData = VariableData[Tile, :, :]
            DataProvider = mule.ArrayDataProvider(NewData)
            Field.set_data_provider(DataProvider)
            Tile += 1

# Intercept the write function to disable validation
def to_file(self, output_file_or_path):
        """
        Write to an output file or path.

        Args:
            * output_file_or_path (string or file-like):
                An open file or filepath. If a path, it is opened and
                closed again afterwards.

        .. Note::
            As part of this the "validate" method will be called. For the
            base :class:`UMFile` class this does nothing, but sub-classes
            may override it to provide specific validation checks.

        """
        # Call validate - to ensure the file about to be written out doesn't
        # contain obvious errors.  This is done here before any new file is
        # created so that we don't create a blank file if the validation fails
        if isinstance(output_file_or_path, six.string_types):
            self.validate(filename=output_file_or_path, warn=True)
        else:
            self.validate(filename=output_file_or_path.name, warn=True)

        if isinstance(output_file_or_path, six.string_types):
            with open(output_file_or_path, 'wb') as output_file:
                self._write_to_file(output_file)
        else:
            self._write_to_file(output_file_or_path)

if __name__ == '__main__':
    FieldsFile = mule.FieldsFile.from_file('PI-02-WithLUH3VegetationMap_2025-03-14.astart')
    STASHmasterBase = mule.STASHmaster.from_file('/g/data/access/umdir/vn7.3/ctldata/STASHmaster/STASHmaster_A')
    STASHmasterExt = mule.STASHmaster.from_file('/g/data/rp23/experiments/2024-03-12_CABLE4-dev/lw5085/CABLE-as-ACCESS/prefix.PRESM_A')
    STASHmasterBase.update(STASHmasterExt)
    FieldsFile.attach_stashmaster_info(STASHmasterBase.by_section(0))
    Dataset = xarray.open_dataset('Restart-2025-03-20.nc')

    for Variable in Dataset.data_vars:
        modify_UM_field_by_name(FieldsFile, Dataset, Variable)

    FieldsFile.to_file = to_file
    FieldsFile.to_file(FieldsFile, 'Restart-2025-03-20.astart')
