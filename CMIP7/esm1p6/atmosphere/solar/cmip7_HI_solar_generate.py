from cmip7_ancil_constants import ANCIL_TODAY
from cmip7_ancil_argparse import (
        common_parser,
        constraint_year_parser)

from solar.cmip7_solar import (
        load_cmip7_solar_cube,
        cmip7_solar_dirpath)

from argparse import ArgumentParser
from pathlib import Path

import iris


def parse_args():
    CMIP7_HI_SOLAR_BEG_YEAR = 1850
    CMIP7_HI_SOLAR_END_YEAR = 2023
    ESM_HI_SOLAR_SAVE_FILENAME = 'TSI_CMIP7_ESM'

    parser = ArgumentParser(
            prog='cmip7_HI_solar_generate',
            description=(
                'Generate input files from CMIP7 historical solar forcings'),
            parents=[
                common_parser(),
                constraint_year_parser(
                    beg_year=CMIP7_HI_SOLAR_BEG_YEAR,
                    end_year=CMIP7_HI_SOLAR_END_YEAR)])
    parser.add_argument('--dataset-date-range')
    parser.add_argument(
            '--save-filename',
            default=ESM_HI_SOLAR_SAVE_FILENAME)
    return parser.parse_args()


def cmip7_hi_solar_save(args, cube, save_dirpath):
    # Ensure that the directory exists.
    save_dirpath.mkdir(mode=0o755, parents=True, exist_ok=True)
    save_filepath = save_dirpath / args.save_filename
    with open(save_filepath, 'w') as save_file:
        for year in range(
                args.constraint_beg_year,
                args.constraint_end_year+1):
            year_cons = iris.Constraint(
                        time=lambda cell: cell.point.year == year)
            year_cube = cube.extract(year_cons)
            year_mean = year_cube.collapsed('time', iris.analysis.MEAN).data
            print(year, f'{year_mean:.3f}', file=save_file)


if __name__ == '__main__':

    args = parse_args()

    cmip7_filename = (
            'multiple_input4MIPs_solar_CMIP_'
            f'{args.dataset_version}_gn_{args.dataset_date_range}.nc')
    cmip7_filepath = cmip7_solar_dirpath(args, 'mon') / cmip7_filename

    solar_irradiance_cube = load_cmip7_solar_cube(cmip7_filepath)

    save_dirpath = (
            Path(args.ancil_target_dirname)
            / 'modern'
            / 'historical'
            / 'atmosphere'
            / 'forcing'
            / 'resolution_independent'
            / ANCIL_TODAY)

    cmip7_hi_solar_save(args, solar_irradiance_cube, save_dirpath)
