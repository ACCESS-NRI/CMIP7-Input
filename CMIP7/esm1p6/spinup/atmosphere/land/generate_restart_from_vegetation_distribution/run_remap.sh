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

reference_restart=""
restart_as_netcdf=""
new_vegetation_dist=""
remap_config=""
remapped_restart_as_netcdf=""
output_restart=""

# Add the -s/--stash arguments to scripts 1 and 3 if you don't have access to the defaults

python convert_UM_restart_to_netcdf.py -i ${reference_restart} -o ${restart_as_netcdf}
python remap_vegetation.py -i ${restart_as_netcdf} -o ${remapped_restart_as_netcdf} -m ${new_vegetation_dist} -c ${remap_config}
python add_netcdf_fields_to_UM_restart.py -i ${remapped_restart_as_netcdf} -o ${output_restart}
