# *****************************COPYRIGHT******************************
# (C) Crown copyright Met Office. All rights reserved.
# For further details please refer to the file LICENCE.txt
# which you should have received as part of this distribution.
# *****************************COPYRIGHT******************************
#
# This file is part of Mule.
#
# Mule is free software: you can redistribute it and/or modify it under
# the terms of the Modified BSD License, as published by the
# Open Source Initiative.
#
# Mule is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Modified BSD License for more details.
#
# You should have received a copy of the Modified BSD License
# along with Mule.  If not, see <http://opensource.org/licenses/BSD-3-Clause>.

"""
This module provides a set of common validation functions.  Generally the
different file classes don't have the exact same requirements, but since a
lot of the validation logic is very similar it is contained here.

"""
from __future__ import (absolute_import, division, print_function)

import mule
import numpy as np
import warnings
from collections import defaultdict
from mule.validators import validate_dataset_type, validate_grid_staggering, validate_integer_constants, validate_real_constants, validate_level_dependent_constants, validate_regular_field


def validate_ancil(umf, filename=None, warn=False):
    """
    Main validation method, ensures that certain quantities are the
    expected sizes and different header quantities are self-consistent.

    Kwargs:
        * filename:
            If provided, this filename will be included in any
            validation error messages raised by this method.
        * warn:
            If True, issue a warning rather than a failure in the event
            that the object fails to validate.

    """
    # Change the component list into a dictionary to make it easier to
    # access components later:
    component_dict = dict(umf.COMPONENTS)

    # Error messages will be accumulated in this list, so that they
    # can all be issued at once (instead of stopping after the first)
    validation_errors = []

    # File must have its dataset_type set correctly
    validation_errors += validate_dataset_type(umf, umf.DATASET_TYPES)

    if (umf.fixed_length_header.vert_coord_type == 4 and
            umf.fixed_length_header.dataset_type == 4):
        # For depth ancillaries, can have a grid staggering of 2, 3 or 6:
        validation_errors += validate_grid_staggering(umf, (2, 3, 6))
    else:
        # But in general, only grid-staggerings of 3 (NewDynamics) or 6
        # (ENDGame) are valid
        validation_errors += validate_grid_staggering(umf, (3, 6))

    # Integer and real constants are mandatory and have particular
    # lengths that must be matched
    validation_errors += (
        validate_integer_constants(
            umf, component_dict["integer_constants"].CREATE_DIMS[0]))

    validation_errors += (
        validate_real_constants(
            umf, component_dict["real_constants"].CREATE_DIMS[0]))

    # Only continue if no errors have been raised so far (the remaining
    # checks are unlikely to work without the above passing)
    if not validation_errors:

        # Level dependent constants also mandatory
        if umf.fixed_length_header.dataset_type == 4:
            # Ancils use a different element to specify the level count
            num_levels = umf.integer_constants.num_levels + 1
        else:
            num_levels = umf.integer_constants.num_p_levels + 1
        validation_errors += (
            validate_level_dependent_constants(
                umf, (num_levels, component_dict[
                    "level_dependent_constants"].CREATE_DIMS[1])))

        # Sizes for row dependent constants (if present)
        if umf.row_dependent_constants is not None:
            dim1 = umf.integer_constants.num_rows
            # ENDGame row dependent constants have an extra point
            if umf.fixed_length_header.grid_staggering == 6:
                dim1 += 1
            validation_errors += (
                validate_row_dependent_constants(
                    umf, (dim1, component_dict[
                        "row_dependent_constants"].CREATE_DIMS[1])))

        # Sizes for column dependent constants (if present)
        if umf.column_dependent_constants is not None:
            validation_errors += (
                validate_column_dependent_constants(
                    umf, (umf.integer_constants.num_cols,
                          component_dict[
                              "column_dependent_constants"].CREATE_DIMS[1])))

        # For the fields, a dictionary will be used to accumulate the
        # errors, where the keys are the error messages.  This will allow
        # us to only print each message once (with a list of fields).
        field_validation = defaultdict(list)
        for ifield, field in enumerate(umf.fields):
            if (umf.fixed_length_header.dataset_type in (1, 2)
                    and field.lbrel == mule._INTEGER_MDI):
                # In dumps, some headers are special mean fields
                if (field.lbpack // 1000) != 2:
                    msg = ("Field is special dump field but does not"
                           "have lbpack N4 == 2")
                    field_validation[msg].append(ifield)

            elif field.lbrel not in (2, 3):
                # If the field release number isn't one of the recognised
                # values, or -99 (a missing/padding field) error
                if field.lbrel != -99:
                    msg = "Field has unrecognised release number {0}"
                    field_validation[
                        msg.format(field.lbrel)].append(ifield)
            else:
                # Land packed fields shouldn't set their rows or columns
                if (field.lbpack % 100)//10 == 2:
                    if field.lbrow != 0:
                        msg = ("Field rows not set to zero for land/sea "
                               "packed field")
                        field_validation[msg].append(ifield)

                    if field.lbnpt != 0:
                        msg = ("Field columns not set to zero for "
                               "land/sea packed field")
                        field_validation[msg].append(ifield)

                elif (umf.row_dependent_constants is not None and
                      umf.column_dependent_constants is not None):
                    # Check that the headers are set appropriately for a
                    # variable resolution field
                    for msg in validate_variable_resolution_field(umf, field):
                        field_validation[msg].append(ifield)
                else:
                    # Check that the grids are consistent - if the STASH
                    # entry is available make use of the extra information
                    for msg in validate_regular_field(umf, field):
                        field_validation[msg].append(ifield)

        # Unpick the messages stored in the dictionary, to provide each
        # error once along with a listing of the fields affected
        for field_msg, field_indices in field_validation.items():
            msg = "Field validation failures:\n  Fields ({0})\n{1}"
            field_str = ",".join(
                [str(ind)
                 for ind in field_indices[:min(len(field_indices), 5)]])
            if len(field_indices) > 5:
                field_str += (
                    ", ... {0} total fields".format(len(field_indices)))
            validation_errors.append(
                msg.format(field_str, field_msg))

    # Now either raise an exception or warning with the messages attached.
    if validation_errors:
        if warn:
            msg = ""
            if filename is not None:
                msg = "\nFile: {0}".format(filename)
            msg += "\n" + "\n".join(validation_errors)
            warnings.warn(msg)
        else:
            raise ValidateError(filename, "\n".join(validation_errors))
