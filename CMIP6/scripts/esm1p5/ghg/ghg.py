#---------------------------------------------------------
# Lauren Stevens Aug 2018
# Read in Met Office CMIP6 GHG file and retrive species for ESM CMIP5-style file
#---------------------------------------------------------
#Met Office file:
# YEARS,DUMM0,CO2,CH4,N2O,HFC125,HFC134a,CFC_11,CFC_12,DUMM1,CFC_113,CFC_114,CFC_115,CARB_TET,MCF,HCFC_22,HCFC_141B,HCFC_142B,HALON1211,HALON1202,....
#       ppt   ppm   ppb   ppb   ppt   ppt   ppt   ppt   ppt   ppt   ppt   ppt   ppt   ppt   ppt   ppt   ppt   ppt   ppt   ppt   ppt   ppt   ppt   ppt
#--->
#ESM file:
# YEARS,CO2,CH4,N2O,CFC_11,CFC_12,CFC_113,HCFC_22,HFC125,HFC134a
#      kg/kg  kg/kg  kg/kg  kg/kg  kg/kg  kg/kg  kg/kg  kg/kg  kg/kg  kg/kg
#---------------------------------------------------------
# change units to kg/kg, 1 mg/kg is 1 ppm
# ppm -> 1e-6 kg/kg
# ppb -> 1e-9 kg/kg
# ppt -> 1e-12 kg/kg
# eg MMR =ppm(gas)/ (mol. weight(dry air)/mol. weight(gas) ) /10^6
#---------------------------------------------------------

import pandas as pd

### read in, delim by whitespace, remove header (skiprows), index by YEARS
fil =pd.read_csv('trgas_rcp_historical.dat',delim_whitespace=True,index_col='YEARS',skiprows=13)
### select species, need to use () for correct order
data=fil.loc[:,('CO2','CH4','N2O','CFC_11','CFC_12','CFC_113','HCFC_22','HFC125','HFC134a')]
### change units to kg/kg
data=data*((44.01/29.)*1e-6,(16.04/29.)*1e-9,(44.013/29.)*1e-9,(137.37/29.)*1e-12,(120.91/29.)*1e-12,(187.375/29.)*1e-12,(86.47/29.)*1e-12,(120.02/29.)*1e-12,(102.03/29.)*1e-12)
### format & output
pd.set_option('display.float_format','{:.6e}'.format)
#pd.set_option('display.float_format','{:4.1f}'.format)
#fil.index=fil.index.astype('float64')
text=data.to_string()
fout=open('trgas_rcp_hist_ESM.dat','w')
fout.writelines(text)
fout.close()

#---------------------------------------------------------
