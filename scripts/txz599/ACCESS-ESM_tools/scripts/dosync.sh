#!/bin/bash

#PBS -P p66
#PBS -q copyq
#PBS -l ncpus=1
#PBS -l walltime=1:00:00
#PBS -l mem=4gb
#PBS -l storage=scratch/p66

rsync -avu /raijin/short/p66/txz599/data /scratch/p66/txz599/
