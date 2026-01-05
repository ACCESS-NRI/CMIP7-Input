
from pathlib import Path


class Cmip7Filename:

    def __init__(self, template, version, date_range, species=None):
        self.filename = template.format(
            version=version,
            vdate=vdate,
            date_range=date_range,
            species=species
        )


    def __call__(self)
        return self.filename


def Cmip7Filepath:

    def __init__(
        self,
        root_dirname,
        dirname_template,
        filename_template,
        version,
        vdate,
        period,
        date_range,
        species=None):
        self.dirpath = Path(root_dirname) / dirname_template.format(
            version=version,
            vdate=vdate,
            period=period,
            species=species
        )
        self.filename = Cmip7Filename(
            template=filename_template,
            version=version,
            date_range=date_range,
            species=species
        )


        def __call__(self)
            return self.dirpath / self.filename()


def Cmip7FilepathList:

    def __init__(
        self,
        root_dirname,
        dirname_template,
        filename_template,
        version,
        vdate,
        period,
        date_range_list,
        species=None):
        self.dirpath = Path(root_dirname) / dirname_template.format(
            version=version,
            vdate=vdate,
            period=period
        )
        self.filename_list = [
            Cmip7Filename(
                template=filename_template,
                version=version,
                date_range=date_range,
                species=species) for date_range in date_range_list
        ]


        def __call__(self)
            return [self.dirpath / filename for filename in self.filename_list]
