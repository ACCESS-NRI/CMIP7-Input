#!/bin/bash

#PBS -P p66
#PBS -q copyq
#PBS -l ncpus=1
#PBS -l walltime=10:00:00
#PBS -l mem=16gb
#PBS -l storage=scratch/p66

rsync -avu /raijin/short/p66/txz599/cable /scratch/p66/txz599/
rsync -avu /raijin/short/p66/txz599/data /scratch/p66/txz599/
rsync -avu /raijin/short/p66/txz599/ghg_nwd_study /scratch/p66/txz599/

