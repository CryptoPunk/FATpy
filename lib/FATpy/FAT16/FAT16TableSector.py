from ..Sector import Sector
class FAT16TableSector(Sector):
    def __init__(self,*args,**kwargs):
        Sector.__init__(self,*args,**kwargs)
        self.x = 0

    def __getitem__(self,key):
        return self.getWORD(key*2)

    def __len__(self):
        return len(self._data)/2

    def __iter__(self):
        return self

    def next(self):
        if (self.x >= len(self)):
            raise StopIteration()
        self.x += 1
        return self[self.x-1]
