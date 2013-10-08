from .Sector import Sector

class Partition():
    def __init__(self,partition):
        self._fh = partition
        self.readBootSector()
        self.readFAT()
        self.readROOT()

    def readSector(self,where=None):
        if where is not None:
            self.seekSector(where)
        return Sector(self._fh.read(self.boot_sector.bps))

    def seekSector(self,where):
        self._fh.seek(where * self.boot_sector.bps)

    def readBootSector(self):
        raise Exception("Unimplemented!")

    def readFAT(self):
        raise Exception("Unimplemented!")

    def readROOT(self):
        raise Exception("Unimplemented!")
