#PBS -P rp23
#PBS -N remap_veg
#PBS -q normal
#PBS -l walltime=2:00:00
#PBS -l mem=8GB
#PBS -l ncpus=1
#PBS -l storage=gdata/rp23+gdata/xp65+gdata/p66+gdata/vk83+gdata/access
#PBS -l wd

module use /g/data/xp65/public/modules
module load conda/analysis3
python convert_UM_restart_to_netcdf.py -i /g/data/vk83/configurations/inputs/access-esm1p6/modern/pre-industrial/restart/atmosphere/PI-02.astart-01010101 -o /g/data/p66/lw5085/ACCESS-ESM1p6-restarts/ESM1p6-atmosphere-restart.nc
python remap_vegetation.py -i /g/data/p66/lw5085/ACCESS-ESM1p6-restarts/ESM1p6-atmosphere-restart.nc -o /g/data/p66/lw5085/ACCESS-ESM1p6-restarts/ESM1p6-remapped-for-LUH3.nc -m newvegfrac.1850-2024.nc -c config-LUH3-2025-03-14.yaml
python add_netcdf_fields_to_UM_restart.py
