from pathlib import Path

import iris


def cmip7_solar_dirpath(args, period):
    return (
        Path(args.cmip7_source_data_dirname)
        / 'SOLARIS-HEPPA'
        / args.dataset_version
        / 'atmos'
        / period
        / 'multiple'
        / 'gn'
        / args.dataset_vdate)


def load_cmip7_solar_cube(path):
    cubelist = iris.load(path)
    name_constraint = iris.Constraint(name='solar_irradiance')
    return cubelist.extract_cube(name_constraint)
