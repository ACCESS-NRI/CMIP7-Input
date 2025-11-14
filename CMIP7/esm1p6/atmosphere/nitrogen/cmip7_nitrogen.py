from pathlib import Path

NITROGEN_SPECIES = ("drynhx", "drynoy", "wetnhx", "wetnoy")
"""
As per https://forum.access-hive.org.au/t/proposed-changes-to-variable-names-in-um-netcdf-conversion/4599
m01s03i884 is NITROGEN DEPOSITION 
"""
NITROGEN_STASH_SECTION = 3
NITROGEN_STASH_ITEM = 884


def cmip7_nitrogen_dirpath(args, period, species):
    return (
        Path(args.cmip7_source_data_dirname)
        / "FZJ"
        / args.dataset_version
        / "atmos"
        / period
        / species
        / "gn"
        / args.dataset_vdate
    )
