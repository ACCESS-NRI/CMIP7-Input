from pathlib import Path

NITROGEN_SPECIES = ("drynhx", "drynoy", "wetnhx", "wetnoy")
"""
The STASH code to use is m01s00i884 NITROGEN DEPOSITION as per
https://github.com/ACCESS-NRI/access-esm1.6-configs/blob/dev-preindustrial%2Bconcentrations/atmosphere/prefix.PRESM_A#L711
"""
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
