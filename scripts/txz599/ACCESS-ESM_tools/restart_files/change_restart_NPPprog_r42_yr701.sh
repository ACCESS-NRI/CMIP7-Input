#!/bin/bash

module rm python
module load python/2.7.6
module use ~access/modules
module load pythonlib/umfile_utils

cp vaoid.astart-cable_NPPprog PI-C2C-1p5r42.astart-07010101_NPPprog
python ../python/subset_um.py PI-C2C-1p5r42.astart-07010101 PI-C2C-1p5r42.astart-07010101_essential

IFS=$'\n' read -d '' -r -a lines < 'PI-C2C-1p5r9.astart-05910101_fields' # array of lines

size=${#lines[@]} # length of array lines
echo $size

for i in {0..256}
do
    echo ${lines[i]}
    dummy=(${lines[i]})
    fnumber=`printf "%4.4i" ${dummy[1]}`
    echo $fnumber
    python ../python/um_copy_field.py -i PI-C2C-1p5r42.astart-07010101_essential -o PI-C2C-1p5r42.astart-07010101_NPPprog -v $fnumber
done

# copy 1850 vegetation fractions and thinning ratio
python ../python/um_replace_field_multilevel.py -v 835 -V fraction -n /g/data1a/p66/txz599/data/luc_hist_maps/cableCMIP6_LC_1850.nc PI-C2C-1p5r42.astart-07010101_NPPprog
python ../python/um_replace_field_multilevel.py -v 216 -V fraction -n /g/data1a/p66/txz599/data/luc_hist_maps/cableCMIP6_LC_1850.nc PI-C2C-1p5r42.astart-07010101_NPPprog
python ../python/um_replace_field_multilevel.py -v 916 -V thinRatio -n /g/data1a/p66/txz599/data/luc_hist_thinning/cableCMIP6_thin_1850.nc PI-C2C-1p5r42.astart-07010101_NPPprog
