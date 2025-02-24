import iris, os, sys
import numpy as np
iris.FUTURE.cell_datetime_objects = True

timeserfile=os.environ.get('timeserfile')
templatefile=os.environ.get('templatefile')
outfile=os.environ.get('outfile')
year=int(os.environ.get('year'))

timeser=iris.load(timeserfile)
template=iris.load(templatefile)

t_idxs=[]
for i,t in enumerate(timeser[0].coord('time')):
    if t.cell(0).point.year == year:
        print(i,t.cell(0).point)
        t_idxs.append(i)

print(t_idxs[0],t_idxs[-1])

cyear=template[0]
cyear.data=timeser[0].data[t_idxs[0]:t_idxs[-1]+1]


iris.save(cyear,'{}/{}_tmp.nc'.format(year,outfile))
