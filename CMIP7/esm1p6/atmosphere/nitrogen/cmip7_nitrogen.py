from pathlib import Path

NITROGEN_SPECIES = ("drynhx", "drynoy", "wetnhx", "wetnoy")
NITROGEN_STASH_ITEM = 447  # m01s00i447 is NITROGEN DEPOSITION (kgN/m2/s)


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
