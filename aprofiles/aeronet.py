# @author Augustin Mortier
# @desc A-Profiles - AeronetsData class


class AeronetData:
    """Base class representing profiles data returned by :class:`aprofiles.io.reader.ReadAeronet`."""

    def __init__(self, data):
        self.data = data
        raise NotImplementedError("AeronetData is not implemented yet")

def _main():
    pass

if __name__ == "__main__":
    _main()
