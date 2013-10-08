from ..Partition import Partition
from ..ClusterChain import ClusterChain
from ..Cluster import Cluster
from ..Sector import Sector
from .FAT16Table import FAT16Table
from .FAT16TableSector import FAT16TableSector
from .FAT16BootSector import FAT16BootSector
from .FAT16Directory import FAT16Directory
class FAT16Partition(Partition):
    def readFAT(self):
        self.fats = []
        self.seekSector(self.boot_sector.reserved_sectors)

        for x in range(self.boot_sector.fat_copies):
            fat = FAT16Table()

            for y in range(self.boot_sector.sectors_per_fat):
                fat.appendSector(self.readFAT16TableSector())

            self.fats.append(fat)
        self.fat = self.fats[0]

    def readFAT16TableSector(self,where=None):
        if where is not None:
            self.seekSector(where)
        return FAT16TableSector(self._fh.read(self.boot_sector.bps))

    def readBootSector(self):
        self.boot_sector = FAT16BootSector(self._fh.read(512))

    def readROOT(self):
        root_sectors = (self.boot_sector.root_entries*32)/self.boot_sector.bps
        self.seekSector(self.boot_sector.reserved_sectors + self.boot_sector.sectors_per_fat * self.boot_sector.fat_copies)
        self.root = FAT16Directory([self.readSector() for x in range(root_sectors)])

    def getClusterChain(self,key):
        chain = [key]
        while self.fat[chain[-1]] != self.fat.end_of_cluster_chain:
            chain.append(self.fat[chain[-1]])
        return ClusterChain([self.getCluster(x) for x in chain])

    def getCluster(self,key):
        root_start = self.boot_sector.reserved_sectors + self.boot_sector.sectors_per_fat * self.boot_sector.fat_copies
        root_size = (self.boot_sector.root_entries*32)/self.boot_sector.bps
        offset = root_start+root_size-2
        offset += key
        return Cluster([self.readSector(offset+x) for x in range(self.boot_sector.spc)])

    def getDirectory(self,key):
      return FAT16Directory(self.getClusterChain(key))
